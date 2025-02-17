import grpc
from generated import key_value_pb2, key_value_pb2_grpc
import random

# Danh sách các node có thể kết nối
NODES = ["localhost:50051", "localhost:50052", "localhost:50053"]

def check_ping(node):
    # Kiểm tra xem node có sẵn sàng kết nối
    try:
        with grpc.insecure_channel(node) as channel:
            stub = key_value_pb2_grpc.KeyValueStoreStub(channel)
            response = stub.Get(key_value_pb2.GetRequest(key="ping"))
            if response.success:
                return True
            else: 
                return False
    except grpc.RpcError as e:
        return False


def get_stub():
    # chọn một node hoạt động
    available_nodes = [node for node in NODES if check_ping(node)]
    if not available_nodes:
        print("No available nodes! Exiting.")
        exit(1) # Dừng chương trình nếu không có node nào khả dụng
    node = random.choice(available_nodes) # chon ngẫu nhiên từ danh sách node khả dụng
    print(f"Using node: {node}")
    channel = grpc.insecure_channel(node)
    return key_value_pb2_grpc.KeyValueStoreStub(channel)

def put(key, value):
    stub = get_stub()
    response = stub.Put(key_value_pb2.PutRequest(key=key, value=value))
    print(f"Put: {response.message}")

def get(key):
    stub = get_stub()
    response = stub.Get(key_value_pb2.GetRequest(key=key))
    print(f"Get: {response.value}")

def delete(key):
    stub = get_stub()
    response = stub.Delete(key_value_pb2.DeleteRequest(key=key))
    print(f"Delete: {response.message}")

def update(key, new_value):
    stub = get_stub()
    response = stub.Update(key_value_pb2.UpdateRequest(key=key, new_value=new_value))
    print(f"Update: {response.message}")

def main():
    while True:
        # Hiển thị menu và nhận lựa chọn
        choice = input("\n1. Put | 2. Get | 3. Delete | 4. Update | 5. Exit: ")
        
        if choice == '1':  # PUT
            key = input("Key: ")
            value = input("Value: ")
            put(key, value)
        elif choice == '2':  # GET
            key = input("Key: ")
            get(key)
        elif choice == '3':  # DELETE
            key = input("Key: ")
            delete(key)
        elif choice == '4':  # UPDATE
            key = input("Key: ")
            new_value = input("New Value: ")
            update(key, new_value)
        elif choice == '5':  # Exit
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please choose again.")



if __name__ == "__main__":
    main()