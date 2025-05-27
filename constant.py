# constant.py

class AppConstants:
    VERSION = "1.0"
    VERSION_DATE = "2025年5月"

    THINGS_LEVEL_DIC = {
        0: '重要并且紧急',
        1: '不重要但紧急',
        2: '重要但不紧急',
        3: '不重要不紧急'
    }

    THINGS_LEVEL_DIC_OP = {
        '重要并且紧急': 0,
        '不重要但紧急': 1,
        '重要但不紧急': 2,
        '不重要不紧急': 3
    }

    COMBO_VALUES = (
        '今日待办事项',
        '全部待办事项',
        '重要并且紧急',
        '不重要但紧急',
        '重要但不紧急',
        '不重要不紧急',
        '已经完成事项',
        '查找结果展示'
    )

    @staticmethod
    def about_text():
        return (
            f"本程序为待办事项管理系统，\n"
            f"请在添加待办选项卡中添加待办事项，\n"
            f"双击待办事项可进行修改和删除操作。\n"
            f"作者：OttoPaglus\n版本：{AppConstants.VERSION} \n日期：{AppConstants.VERSION_DATE}"
        )
