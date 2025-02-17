from flask import Flask, render_template, request, redirect, url_for, jsonify
import sys
import os

# Đảm bảo thư mục gốc có thể import các module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import grpc
from generated import key_value_pb2, key_value_pb2_grpc

app = Flask(__name__)

# Danh sách các node có thể kết nối
NODES = ["localhost:50051", "localhost:50052", "localhost:50053"]

def get_stub():
    # chọn một node hoạt động
    available_nodes = [node for node in NODES if check_ping(node)]
    if not available_nodes:
        print("No available nodes! Exiting.")
        exit(1)  # Dừng chương trình nếu không có node nào khả dụng
    node = available_nodes[0]  # Chọn node đầu tiên từ danh sách khả dụng
    print(f"Using node: {node}")
    channel = grpc.insecure_channel(node)
    return key_value_pb2_grpc.KeyValueStoreStub(channel)

def check_ping(node):
    # Kiểm tra xem node có sẵn sàng kết nối
    try:
        with grpc.insecure_channel(node) as channel:
            stub = key_value_pb2_grpc.KeyValueStoreStub(channel)
            response = stub.Get(key_value_pb2.GetRequest(key="ping"))
            return response.success
    except grpc.RpcError:
        return False

@app.route('/')
def index():
    # Trả về trang HTML chính
    return render_template('index.html')

@app.route('/put', methods=['POST'])
def put():
    data = request.get_json()  # Lấy dữ liệu JSON từ request
    key = data.get('key')
    value = data.get('value')
    
    if not key or not value:
        return jsonify({"message": "Key and Value are required!"}), 400
    
    stub = get_stub()
    response = stub.Put(key_value_pb2.PutRequest(key=key, value=value))
    return jsonify({"message": response.message})

@app.route('/get', methods=['POST'])
def get():
    data = request.get_json()  # Lấy dữ liệu JSON từ request
    key = data.get('key')
    
    if not key:
        return jsonify({"message": "Key is required!"}), 400
    
    stub = get_stub()
    response = stub.Get(key_value_pb2.GetRequest(key=key))
    return jsonify({"value": response.value})

@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()  # Lấy dữ liệu JSON từ request
    key = data.get('key')
    
    if not key:
        return jsonify({"message": "Key is required!"}), 400
    
    stub = get_stub()
    response = stub.Delete(key_value_pb2.DeleteRequest(key=key))
    return jsonify({"message": response.message})

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()  # Lấy dữ liệu JSON từ request
    key = data.get('key')
    new_value = data.get('new_value')
    
    if not key or not new_value:
        return jsonify({"message": "Key and New Value are required!"}), 400
    
    stub = get_stub()
    response = stub.Update(key_value_pb2.UpdateRequest(key=key, new_value=new_value))
    return jsonify({"message": response.message})

if __name__ == '__main__':
    app.run(debug=True)