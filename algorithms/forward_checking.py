import copy

def solve_forward_checking(nodes, adj, colors):
    assignment = {}  # Biến đã gán giá trị
    domains = {n: list(colors) for n in nodes} # Miền giá trị ban đầu
    # Trạng thái khởi tạo
    yield {
        "action": "init", 
        "assignment": {}, 
        "log": f"Biểu diễn dưới dạng CSP:\n- Biến: {{{', '.join(nodes)}}}\n- Miền giá trị: {{{', '.join(colors)}}}\n\nÁp dụng Backtracking + Forward Checking:\nBước 1: Assignment={{}}"
    }
    
    def backtrack(curr_domains, step_count):
        if len(assignment) == len(nodes):
            yield {"action": "done", "assignment": assignment.copy()}
            return True
         # Chọn biến chưa gán đầu tiên
        node = [n for n in nodes if n not in assignment][0]
        yield {
            "action": "select_var", 
            "node": node, 
            "assignment": assignment.copy(),
            "log": f"Bước {step_count}: Chọn biến {'đầu tiên' if step_count == 2 else 'tiếp theo'}:\n- Chọn {node}"
        }
         # Thử từng giá trị trong miền
        for color in curr_domains[node]:
            yield {
                "action": "try_color", 
                "node": node, 
                "color": color, 
                "assignment": assignment.copy(),
                "log": f"- Chọn giá trị: {node}={color.capitalize()}"
            }
            # Gán giá trị cho biến
            assignment[node] = color
            new_domains = copy.deepcopy(curr_domains)
            ass_str = ", ".join([f"{k}={v.lower()}" for k, v in assignment.items()])
            yield {
                "action": "valid", 
                "node": node, 
                "color": color, 
                "assignment": assignment.copy(),
                "log": f"- Kiểm tra ràng buộc => hợp lệ\nAssignment={{{ass_str}}}"
            }
            # Forward Checking: loại bỏ màu vừa gán khỏi miền các đỉnh kề
            wipeout = False
            updates = []
            for neighbor in adj[node]:
                if neighbor not in assignment and color in new_domains[neighbor]:
                    new_domains[neighbor].remove(color)
                    domain_str = ", ".join([c.lower() for c in new_domains[neighbor]])
                    updates.append(f"+ Miền giá trị của {neighbor} = {{{domain_str}}}")
                    if not new_domains[neighbor]:
                        wipeout = True    
            # cập nhật domain    
            if updates:
                log_msg = "- Update lại domain của các biến chưa được gán\nvà có ràng buộc với biến vừa được gán giá trị:\n" + "\n".join(updates)
                yield {
                    "action": "fc_update", 
                    "node": node, 
                    "color": color, 
                    "assignment": assignment.copy(),
                    "log": log_msg
                } 
             # Nếu xuất hiện miền rỗng -> quay lui
            if wipeout:
                yield {
                    "action": "fc_wipeout", 
                    "node": node, 
                    "assignment": assignment.copy(),
                    "log": "=> [Lỗi] Tồn tại miền giá trị rỗng -> Quay lui!"
                }
                del assignment[node]
                continue
            # Đệ quy gán biến tiếp theo
            if (yield from backtrack(new_domains, step_count + 1)):
                return True  
            # Quay lui nếu nhánh hiện tại thất bại   
            del assignment[node]
            ass_str = ", ".join([f"{k}={v.lower()}" for k, v in assignment.items()])
            yield {
                "action": "backtrack", 
                "node": node, 
                "assignment": assignment.copy(),
                "log": f"- [Quay lui] Khôi phục domain, bỏ màu của {node}\nAssignment={{{ass_str}}}"
            }
        return False
    yield from backtrack(domains, 2)