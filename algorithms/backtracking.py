def solve_backtracking(nodes, adj, colors):
    assignment = {} # Lưu các biến đã được gán giá trị
    yield {
        "action": "init", 
        "assignment": {}, 
        "log": "Áp dụng Backtracking:\nBước 1: Assignment={}"
    }
    
    def backtrack(step_count):
        if len(assignment) == len(nodes):
            yield {"action": "done", "assignment": assignment.copy()}
            return True
        # Chọn biến chưa gán đầu tiên
        unassigned = [n for n in nodes if n not in assignment]
        node = unassigned[0] 
        yield {
            "action": "select_var", 
            "node": node, 
            "assignment": assignment.copy(),
            "log": f"Bước {step_count}: Chọn biến {'đầu tiên' if step_count == 2 else 'tiếp theo'}:\n- Chọn {node}"
        }
        # Thử từng giá trị trong miền
        for color in colors:
            yield {
                "action": "try_color", 
                "node": node, 
                "color": color, 
                "assignment": assignment.copy(),
                "log": f"- Chọn giá trị để gán cho {node} bằng cách thử: {node} = {color.lower()}"
            }
            # Kiểm tra ràng buộc với các đỉnh kề
            is_safe = all(assignment.get(neighbor) != color for neighbor in adj[node])
            if is_safe:
                # Gán giá trị cho biến
                assignment[node] = color
                ass_str = ", ".join([f"{k}={v.lower()}" for k, v in assignment.items()])
                yield {
                    "action": "valid", 
                    "node": node, 
                    "color": color, 
                    "assignment": assignment.copy(),
                    "log": f"- Kiểm tra ràng buộc: hợp lệ\nAssignment={{{ass_str}}}"
                }  
                # Đệ quy cho biến tiếp theo
                if (yield from backtrack(step_count + 1)):
                    return True     
                # Quay lui nếu nhánh hiện tại thất bại     
                del assignment[node]
                ass_str = ", ".join([f"{k}={v.lower()}" for k, v in assignment.items()])
                yield {
                    "action": "backtrack", 
                    "node": node, 
                    "assignment": assignment.copy(),
                    "log": f"- [Quay lui] Thử giá trị khác do nhánh dưới bế tắc.\nAssignment={{{ass_str}}}"
                }
            else:
                # Giá trị vi phạm ràng buộc
                yield {
                    "action": "invalid", 
                    "node": node, 
                    "color": color, 
                    "assignment": assignment.copy(),
                    "log": "- Kiểm tra ràng buộc => ko hợp lệ"
                }  
        # Không tìm được nghiệm ở nhánh hiện tại        
        return False
    yield from backtrack(2)