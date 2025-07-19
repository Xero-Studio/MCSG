#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查qfluentwidgets可用组件
"""

def check_qfluentwidgets_components():
    """检查qfluentwidgets中可用的组件"""
    try:
        import qfluentwidgets
        print(f"qfluentwidgets 版本检查...")
        
        # 检查常用组件
        components_to_check = [
            'FluentWindow', 'NavigationItemPosition', 'FluentIcon',
            'PushButton', 'LineEdit', 'SpinBox', 'CheckBox', 'TextEdit',
            'ComboBox', 'InfoBar', 'InfoBarPosition', 'MessageBox',
            'CardWidget', 'HeaderCardWidget', 'SimpleCardWidget',
            'StrongBodyLabel', 'BodyLabel', 'CaptionLabel',
            'TabWidget', 'Pivot', 'SegmentedWidget',
            'Slider', 'setTheme', 'Theme'
        ]
        
        available_components = []
        missing_components = []
        
        for component in components_to_check:
            try:
                getattr(qfluentwidgets, component)
                available_components.append(component)
                print(f"✓ {component}")
            except AttributeError:
                missing_components.append(component)
                print(f"✗ {component}")
        
        print(f"\n可用组件: {len(available_components)}")
        print(f"缺失组件: {len(missing_components)}")
        
        if missing_components:
            print(f"\n缺失的组件: {', '.join(missing_components)}")
        
        # 检查选项卡相关组件
        print(f"\n=== 选项卡组件检查 ===")
        tab_components = ['TabWidget', 'Pivot', 'SegmentedWidget']
        available_tab = None
        
        for tab_comp in tab_components:
            try:
                getattr(qfluentwidgets, tab_comp)
                print(f"✓ {tab_comp} 可用")
                if available_tab is None:
                    available_tab = tab_comp
            except AttributeError:
                print(f"✗ {tab_comp} 不可用")
        
        if available_tab:
            print(f"\n推荐使用: {available_tab}")
        else:
            print(f"\n建议使用 PyQt5.QtWidgets.QTabWidget")
        
        return available_tab
        
    except ImportError as e:
        print(f"qfluentwidgets 导入失败: {e}")
        return None

if __name__ == "__main__":
    check_qfluentwidgets_components()