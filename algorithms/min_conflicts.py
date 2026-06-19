import random

def solve_min_conflicts(nodes, adj, colors, max_steps=100):
    # Khởi tạo ngẫu nhiên
    assignment = {n: random.choice(colors) for n in nodes}
    yield {
        "action": "init", 
        "assignment": assignment.copy(), 
        "log": "Khởi tạo thuật toán Min-Conflicts (Local Search)\nTiến hành gán màu ngẫu nhiên cho toàn bộ bản đồ..."
    }
    step_count = 1
    while step_count <= max_steps:
        # 1. Tìm các đỉnh bị xung đột (vi phạm ràng buộc)
        conflicted_vars = []
        for u in nodes:
            for v in adj[u]:
                if assignment[u] == assignment[v]:
                    conflicted_vars.append(u)
                    break # Có ít nhất 1 xung đột là đưa vào danh sách lỗi
        if not conflicted_vars:
            yield {
                "action": "done", 
                "assignment": assignment.copy(), 
                "log": f"Trạng thái hợp lệ! Đã giải quyết xong sau {step_count - 1} bước."
            }
            return True
        # 2. Chọn ngẫu nhiên 1 đỉnh bị lỗi
        var = random.choice(conflicted_vars)
        yield {
            "action": "select_var", 
            "node": var, 
            "assignment": assignment.copy(), 
            "log": f"\nBước {step_count}: Phát hiện xung đột!\n👉 Chọn biến bị lỗi: {var}"
        }
        # 3. Thử các màu để tìm màu có ít xung đột nhất
        best_color = assignment[var]
        min_conflicts_count = float('inf')
        for color in colors:
            yield {
                "action": "try_color", 
                "node": var, 
                "color": color, 
                "assignment": assignment.copy(), 
                "log": f"   Thử màu: {var} = {color}"
            }
            # Đếm số lượng hàng xóm bị trùng màu
            count = sum(1 for neighbor in adj[var] if assignment.get(neighbor) == color)
            if count < min_conflicts_count:
                min_conflicts_count = count
                best_color = color
        # 4. Cập nhật màu tốt nhất
        assignment[var] = best_color
        if min_conflicts_count == 0:
            log_msg = f"   Kiểm tra ràng buộc cục bộ: hợp lệ (Gán {var} = {best_color})"
        else:
            log_msg = f"   Gán {var} = {best_color} (Còn {min_conflicts_count} xung đột, tiếp tục sửa)"
        yield {
            "action": "valid", 
            "node": var, 
            "color": best_color, 
            "assignment": assignment.copy(), 
            "log": log_msg
        }
        step_count += 1
    yield {
        "action": "done", 
        "assignment": assignment.copy(), 
        "log": "[Lỗi] Vượt quá số bước lặp tối đa. Quay lui hoặc khởi tạo lại."
    }
    return False