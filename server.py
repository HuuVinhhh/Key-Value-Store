import grpc
import sys
import threading
import time
from concurrent import futures
from generated import key_value_pb2, key_value_pb2_grpc


# Danh sách các nodes trong hệ thống
NODES = ["localhost:50051", "localhost:50052", "localhost:50053"]

class KeyValueStoreServicer(key_value_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, node_id):
        self.node_id = node_id
        self.data_store = {}
        self.alive_nodes = set(NODES) # Danh sách các node đang hoạt động
        self.dead_nodes = set() # Danh sách các node bị lỗi

        #Bắt đầu gửi heartbeat định kỳ
        self.start_heartbeat()

        #Khi khởi động, đồng bộ lại dữ liệu
        self.sync_data()

    def Put(self, request, context):
        if request.key in self.data_store:
            return key_value_pb2.Response(success=True, message="Key already exists, Using another Key or Update")
        
        self.data_store[request.key] = request.value
        self.replicate_to_other_nodes(request.key, request.value) # Đồng bộ với nodes khác
        return key_value_pb2.Response(success=True, message="Put Success")
    
    def Get(self, request, context):
        if request.key == "ping":
            return key_value_pb2.GetResponse(success=True, value="pong")  # Trả về "pong" khi key="ping"
        
        # Kiểm tra dữ liệu trong node hiện tại
        if request.key in self.data_store:
            print(f"Found Key {request.key}")
            return key_value_pb2.GetResponse(success=True, value=self.data_store[request.key])

        # Nếu không có dữ liệu, tìm trong các node khác
        lookup_result = self.lookup_key(request.key)

        if lookup_result is not None:
            return key_value_pb2.GetResponse(success=True, value=lookup_result)
        
        # Nếu không node nào có dữ liệu
        print(f"Key {request.key} Not Found")
        return key_value_pb2.GetResponse(success=False, value="Key Not Found")
    
    def Delete(self, request, context):
        if request.key in self.data_store:
            del self.data_store[request.key]
            self.replicate_delete_to_other_nodes(request.key) # Đồng bộ xóa với các node khác
            return key_value_pb2.Response(success=True, message="Delete Success")
        return key_value_pb2.Response(success=False, message="Key Not Found")
    
    def Update(self, request, context):
        # Cập nhật dữ liệu nếu key tồn tại
        if request.key in self.data_store:
            old_value = self.data_store[request.key]
            if old_value != request.new_value: # Chỉ cập nhật nếu giá trị thay đổi
                self.data_store[request.key] = request.new_value

                # Chỉ gửi relication khi thực sự có thay đổi
                self.replicate_to_other_nodes(request.key, request.new_value) # Đồng bộ với node khác
                return key_value_pb2.Response(success=True, message="Update Success")
            else:
                return key_value_pb2.Response(success=False, message="No Change in value")

        return key_value_pb2.Response(success=False, message="Key Not Found") 
    
    def Replicate(self, request, context):
        self.data_store[request.key] = request.value
        return key_value_pb2.Response(success=True, message="Replication Success")
    
    def DeleteReplication(self, request, context):
        if request.key in self.data_store:
            del self.data_store[request.key]
        return key_value_pb2.Response(success=True, message="Delete Replication Success")

    def replicate_to_other_nodes(self, key, value):
        # Gửi dữ liệu cập nhật đến các node khác
        for node in self.alive_nodes:
            if node != f"localhost:{self.node_id}": # Không gửi cho chính nó
                try:
                    with grpc.insecure_channel(node) as channel:
                        stub = key_value_pb2_grpc.KeyValueStoreStub(channel)
                        stub.Replicate(key_value_pb2.PutRequest(key=key, value=value))
                        print(f"Node {self.node_id}: Successfully replicated {key} to {node}")
                except Exception as e:
                    print(f"lỗi khi replicate đến {node}: {e}")

    def replicate_delete_to_other_nodes(self, key):
        # Gửi lệnh xóa dữ liệu đến các node khác
        for node in self.alive_nodes:
            if node != f"localhost:{self.node_id}": # Không gửi cho chính nó
                try:
                    with grpc.insecure_channel(node) as channel:
                        stub = key_value_pb2_grpc.KeyValueStoreStub(channel)
                        stub.DeleteReplication(key_value_pb2.DeleteRequest(key=key))
                        print(f"Node {self.node_id}: Successfully deleted {key} from {node}")
                except Exception as e:
                    print(f"Lỗi khi replicate delete đến {node}: {e}")
    
    def lookup_key(self, key):
        # Tìm kiếm key trong node khác
        for node in self.alive_nodes: # chỉ hỏi node còn sống
            if node != f"localhost:{self.node_id}": # Không tìm trong chính nó
                try:
                    with grpc.insecure_channel(node) as channel:
                        stub = key_value_pb2_grpc.KeyValueStoreStub(channel)
                        response = stub.Get(key_value_pb2.GetRequest(key=key))

                        if response.success: # Nếu tìm thấy trả về giá trị
                            print(f"Node {self.node_id}: Found key {key} on {node}, returning value")
                            return response.value
                except grpc.RpcError as e:
                    print(f"Lỗi khi lookup {key} từ {node}:{e}")

            return None # Trả về None nếu không node nào có dữ liệu
    
    def start_heartbeat(self):
        # Gửi heartbeat định kỳ để kiểm tra trạng thái các node
        def heartbeat():
            while True:
                for node in NODES:
                    if node != f"localhost:{self.node_id}": # Không ping chính nó
                        node_status = self.send_heartbeat(node)
                        
                        if node_status:
                            if node in self.dead_nodes:
                                print(f"Node {node} is back online!")
                                self.dead_nodes.discard(node)
                                self.alive_nodes.add(node)
                        else:
                            if node in self.alive_nodes:
                                print(f"Node {node} is down!")
                                self.alive_nodes.discard(node)
                                self.dead_nodes.add(node)

                time.sleep(3) # Gửi heartbeat mỗi 3 giây

        threading.Thread(target=heartbeat, daemon=True).start()

    def send_heartbeat(self, node, retries=3, delay=1):
        # Gửi heartbeat đến một node để kiểm tra xem nó có hoạt động không
        for _ in range(retries):
            try:
                with grpc.insecure_channel(node) as channel:
                    stub = key_value_pb2_grpc.KeyValueStoreStub(channel)
                    response = stub.Heartbeat(key_value_pb2.HeartbeatRequest()) # Gửi yêu cầu heartbeat
                    if response.success:
                        return True  # Nếu node phản hồi, coi như nó hoạt động
            except grpc.RpcError:
                time.sleep(delay) # Đợi 1s trước khi thử lại

        return False # Nếu không phản hồi retries, node đã bị hỏng
        
    def Heartbeat(self, request, context):
        # Trả lời Heartbeat từ các node khác
        return key_value_pb2.HeartbeatResponse(success=True)
    
    def SyncData(self, request, context):
        # Đồng bộ dữ liệu cho node khởi động lại
        return key_value_pb2.SyncResponse(data=self.data_store)
    
    def sync_data(self):
        # Khi node khởi động với dữ liệu trống, đồng bộ lại dữ liệu từ node sống
        if not self.data_store:
            for node in self.alive_nodes:
                if node != f"localhost:{self.node_id}": # Không yêu cầu từ chính nó
                    try:
                        with grpc.insecure_channel(node) as channel:
                            stub = key_value_pb2_grpc.KeyValueStoreStub(channel)
                            response = stub.SyncData(key_value_pb2.SyncRequest())

                            if response.data: # Nếu có dữ liệu từ node khác
                                self.data_store = dict(response.data)
                                print(f"Node {self.node_id} synced data from {node}.")
                                return
                    except grpc.RpcError:
                        continue # Thử tiếp các node khác nếu một node không phản hồi
        

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    key_value_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(port), server)

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server node {port} is running ...")

    server.wait_for_termination()

if __name__ == "__main__":
    # port = sys.argv[1] if len(sys.argv) > 1 else "50051"
    # serve(port)

    # Lấy cổng từ tham số dòng lệnh, nếu không có thì sẽ báo lỗi
    if len(sys.argv) < 2:
        sys.exit(1)
    
    port = sys.argv[1]
    serve(port)

# python server/node.py 50051
# python server/node.py 50052
# python server/node.py 50053