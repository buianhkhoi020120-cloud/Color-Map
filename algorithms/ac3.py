import copy

def solve_ac3(nodes, adj, colors):
    assignment = {}
    # Khởi tạo domain cho tất cả các đỉnh
    domains = {n: list(colors) for n in nodes}
    yield {
        "action": "init", 
        "assignment": {}, 
        "log": f"Biểu diễn dưới dạng CSP:\n- Biến: {{{', '.join(nodes)}}}\n- Miền giá trị: {{{', '.join(colors)}}}\n\nÁp dụng Backtracking kết hợp AC-3 (MAC):"
    }

    # Hàm RM-INCONSISTENT-VALUES
    def rm_inconsistent_values(Xi, Xj, current_domains):
        removed = False
        for x in list(current_domains[Xi]):
            # Trong tô màu bản đồ, ràng buộc là Xi != Xj
            # Không có giá trị y nào thỏa mãn => tức là Domain[Xj] chỉ có duy nhất màu x
            if len(current_domains[Xj]) == 1 and current_domains[Xj][0] == x:
                current_domains[Xi].remove(x)
                removed = True
        return removed

    # Hàm vòng lặp AC-3 dùng queue
    def ac3(queue, current_domains):
        logs = []
        while queue:
            # Lấy (Xi, Xj) ra khỏi queue (Remove-First)
            Xi, Xj = queue.pop(0)
            # Nếu có giá trị bị xóa khỏi domain của Xi
            if rm_inconsistent_values(Xi, Xj, current_domains):
                if not current_domains[Xi]: # Nếu domain rỗng
                    return False, logs + [f"    [!] Domain {Xi} rỗng do AC-3 lan truyền!"]
                logs.append(f"    + AC-3 lan truyền: Domain {Xi} = {{{', '.join([c.lower() for c in current_domains[Xi]])}}}")
                # Thêm lại các cung (Xk, Xi) vào queue với Xk là hàng xóm Xi
                for Xk in adj[Xi]:
                    if Xk != Xj:
                        if (Xk, Xi) not in queue:
                            queue.append((Xk, Xi))
        return True, logs

    def backtrack(curr_domains, step_count):
        if len(assignment) == len(nodes):
            yield {"action": "done", "assignment": assignment.copy()}
            return True
        unassigned = [n for n in nodes if n not in assignment]
        node = unassigned[0]
        yield {
            "action": "select_var", 
            "node": node, 
            "assignment": assignment.copy(),
            "log": f"\nBước {step_count}: Chọn biến:\n- Chọn {node}"
        }
        for color in curr_domains[node]:
            yield {
                "action": "try_color", 
                "node": node, 
                "color": color, 
                "assignment": assignment.copy(),
                "log": f"- Chọn giá trị: {node}={color.capitalize()}"
            }
            assignment[node] = color
            new_domains = copy.deepcopy(curr_domains)
            # Khi đã gán, domain của node này chỉ còn đúng 1 màu đó
            new_domains[node] = [color] 
            ass_str = ", ".join([f"{k}={v.lower()}" for k, v in assignment.items()])
            yield {
                "action": "valid", 
                "node": node, 
                "color": color, 
                "assignment": assignment.copy(),
                "log": f"- Kiểm tra ràng buộc => hợp lệ\nAssignment={{{ass_str}}}"
            }
            # Đẩy tất cả các cung lân cận của node vừa gán vào Queue để AC-3 xử lý
            queue = [(neighbor, node) for neighbor in adj[node] if neighbor not in assignment]
            # Chạy AC-3
            is_consistent, ac3_logs = ac3(queue, new_domains)
            if ac3_logs:
                yield {
                    "action": "fc_update", 
                    "node": node, 
                    "color": color, 
                    "assignment": assignment.copy(),
                    "log": "- Thực thi AC-3 (Arc Consistency):\n" + "\n".join(ac3_logs)
                }
            if not is_consistent:
                yield {
                    "action": "fc_wipeout", 
                    "node": node, 
                    "assignment": assignment.copy(),
                    "log": "=> [Lỗi] AC-3 phát hiện miền giá trị rỗng -> Quay lui!"
                }
                del assignment[node]
                continue
            if (yield from backtrack(new_domains, step_count + 1)):
                return True
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