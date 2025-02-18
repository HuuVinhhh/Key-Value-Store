function handlePut() {
    const key = document.getElementById("put-key").value;
    const value = document.getElementById("put-value").value;
    
    // Kiểm tra nếu trường input không trống
    if (key && value) {
        fetch('/put', {
            method: 'POST',
            body: JSON.stringify({ key, value }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").innerText = data.message;
            document.getElementById("result").innerText = '';
            // Sau khi PUT xong, xóa dữ liệu trong các trường input
            document.getElementById("put-key").value = '';
            document.getElementById("put-value").value = '';
        })
        .catch(error => {
            document.getElementById("message").innerText = 'Error occurred during PUT.';
        });
    } else {
        document.getElementById("message").innerText = 'Please enter both Key and Value.';
    }
}

function handleGet() {
    const key = document.getElementById("get-key").value;
    
    // Kiểm tra nếu key không trống
    if (key) {
        fetch('/get', {
            method: 'POST',
            body: JSON.stringify({ key }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").innerText = '';
            document.getElementById("result").innerText = 'Value: ' + data.value;
            // Sau khi GET xong, xóa dữ liệu trong trường input
            document.getElementById("get-key").value = '';
        })
        .catch(error => {
            document.getElementById("message").innerText = 'Error occurred during GET.';
        });
    } else {
        document.getElementById("message").innerText = 'Please enter Key.';
    }
}

function handleDelete() {
    const key = document.getElementById("delete-key").value;
    
    // Kiểm tra nếu key không trống
    if (key) {
        fetch('/delete', {
            method: 'POST',
            body: JSON.stringify({ key }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").innerText = data.message;
            document.getElementById("result").innerText = '';
            // Sau khi DELETE xong, xóa dữ liệu trong trường input
            document.getElementById("delete-key").value = '';
        })
        .catch(error => {
            document.getElementById("message").innerText = 'Error occurred during DELETE.';
        });
    } else {
        document.getElementById("message").innerText = 'Please enter Key to delete.';
    }
}

function handleUpdate() {
    const key = document.getElementById("update-key").value;
    const newValue = document.getElementById("update-value").value;
    
    // Kiểm tra nếu key và new_value không trống
    if (key && newValue) {
        fetch('/update', {
            method: 'POST',
            body: JSON.stringify({ key, new_value: newValue }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").innerText = data.message;
            document.getElementById("result").innerText = '';
            // Sau khi UPDATE xong, xóa dữ liệu trong các trường input
            document.getElementById("update-key").value = '';
            document.getElementById("update-value").value = '';
        })
        .catch(error => {
            document.getElementById("message").innerText = 'Error occurred during UPDATE.';
        });
    } else {
        document.getElementById("message").innerText = 'Please enter both Key and New Value.';
    }
}