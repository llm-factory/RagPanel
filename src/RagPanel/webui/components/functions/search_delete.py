import gradio as gr
import pandas as pd

def create_search_delete_tab(engine, search_result_state, LOCALES):
    """
    创建搜索删除标签页
    
    Args:
        engine: 搜索引擎实例
        search_result_state: 搜索结果状态
        LOCALES: 本地化文本字典
    
    Returns:
        gr.Blocks: 搜索删除标签页组件
    """
    
    with gr.Blocks() as search_delete_tab:
        # 标题区域
        gr.Markdown(
            f"## {LOCALES['search_delete_tab_title']}",
            elem_classes=["tab-title"]
        )
        
        # 可折叠的使用说明
        with gr.Accordion(
            label=LOCALES["usage_instructions"], 
            open=False,
            elem_classes=["instructions-accordion"]
        ):
            gr.Markdown(
                LOCALES["search_delete_instructions"],
                elem_classes=["instructions-content"]
            )
        
        # 搜索区域
        with gr.Group():
            
            with gr.Row():
                search_box = gr.Textbox(
                    label=LOCALES["query"],
                    placeholder=LOCALES["search_placeholder"],
                    lines=3,
                    scale=4,
                    elem_classes=["search-input"]
                )
            
            with gr.Row():
                with gr.Column(scale=1):
                    search_btn = gr.Button(
                        LOCALES["search_file"],
                        variant="primary",
                        size="lg",
                        elem_classes=["search-button"]
                    )
                
                with gr.Column(scale=1):
                    clear_btn = gr.Button(
                        LOCALES["clear_search"],
                        variant="secondary",
                        size="lg",
                        elem_classes=["clear-button"]
                    )
        
        # 搜索结果和删除区域
        with gr.Group():
            gr.Markdown(
                f"### {LOCALES['search_results_section']}",
                elem_classes=["section-title"]
            )
            
            # 搜索状态显示
            search_status = gr.Markdown(
                LOCALES["search_status_ready"],
                elem_classes=["search-status"]
            )
            
            # 动态渲染搜索结果
            @gr.render(inputs=search_result_state, triggers=[search_result_state.change])
            def show_search_results(docs: pd.DataFrame):
                """动态渲染搜索结果"""
                if docs is not None and len(docs) > 0:
                    # 显示搜索结果统计
                    gr.Markdown(
                        f"**{LOCALES['search_results_found'].format(count=len(docs))}**",
                        elem_classes=["results-count"]
                    )
                    
                    # 搜索结果选择区域
                    with gr.Row():
                        with gr.Column():
                            # 格式化显示内容
                            formatted_choices = [
                                _format_search_result(idx, content) 
                                for idx, content in enumerate(docs["content"].tolist())
                            ]
                            
                            checkbox = gr.Checkboxgroup(
                                choices=formatted_choices,
                                type="index",
                                label=LOCALES["select_file_delete"],
                                elem_classes=["results-checkbox"]
                            )
                    
                    # 批量操作区域
                    with gr.Row():
                        
                        with gr.Column(scale=1):
                            delete_selected_btn = gr.Button(
                                LOCALES["delete_selected"],
                                variant="stop",
                                elem_classes=["delete-selected-button"]
                            )
                    
                    def _handle_delete_selected(selected_indices):
                        """
                        处理删除选中项操作
                        
                        Args:
                            selected_indices: 选中的索引列表
                        
                        Returns:
                            更新后的搜索结果状态
                        """
                        if not selected_indices:
                            gr.Warning(LOCALES["no_items_selected"])
                            return docs
                        
                        try:
                            # 调用后端删除函数，传递索引和当前搜索结果
                            updated_docs = engine.delete(selected_indices, docs)
                            gr.Info(LOCALES["delete_success"].format(count=len(selected_indices)))
                            return updated_docs
                        except Exception as e:
                            gr.Error(LOCALES["delete_error"].format(error=str(e)))
                            return docs
                    
                    
                    delete_selected_btn.click(
                        _handle_delete_selected,
                        inputs=[checkbox],
                        outputs=[search_result_state]
                    )
                    
                else:
                    # 无搜索结果时的显示
                    gr.Markdown(
                        f"ℹ️ {LOCALES['no_search_results']}",
                        elem_classes=["no-results"]
                    )
    
    def _format_search_result(index: int, content: str, max_length: int = 100) -> str:
        """
        格式化搜索结果显示
        
        Args:
            index: 结果索引
            content: 内容文本
            max_length: 最大显示长度
        
        Returns:
            str: 格式化后的显示文本
        """
        truncated_content = content[:max_length] + "..." if len(content) > max_length else content
        return f"[{index + 1}] {truncated_content}"
    
    def _handle_search(query: str):
        """
        处理搜索操作
        
        Args:
            query: 搜索查询
        
        Returns:
            tuple: (搜索结果, 状态信息)
        """
        if not query.strip():
            gr.Warning(LOCALES["empty_query_warning"])
            return None, LOCALES["search_status_ready"]
        
        try:
            # 执行搜索
            results = engine.search(query)
            status = LOCALES["search_status_completed"].format(
                count=len(results) if results is not None else 0
            )
            return results, status
        except Exception as e:
            gr.Error(LOCALES["search_error"].format(error=str(e)))
            return None, LOCALES["search_status_error"]
    
    def _handle_clear():
        """处理清空操作"""
        return "", None, LOCALES["search_status_ready"]
    
    # 绑定主要事件
    search_btn.click(
        _handle_search,
        inputs=[search_box],
        outputs=[search_result_state, search_status]
    )
    
    clear_btn.click(
        _handle_clear,
        outputs=[search_box, search_result_state, search_status]
    )
    
    return search_delete_tab
