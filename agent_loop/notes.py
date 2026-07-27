from pydantic import BaseModel,Field

demo_notes = [
        {"id": 1, "title": "购物清单", "content": "牛奶、鸡蛋"},
        {"id": 2, "title": "笔记", "content": "考试，测试"}
    ]

drafts_approval_required = True

class ToolException(Exception):
    def __init__(self, message:str, code:int = 500) -> None:
        self.code = code
        super().__init__(message)

class NoteNotFoundError(ToolException):
    def __init__(self, message: str, code: int = 404) -> None:
        super().__init__(message, code)

class DraftNotApprovedError(ToolException):
    def __init__(self, message: str, code: int = 401) -> None:
        super().__init__(message, code)

class ValidationError(ToolException):
    def __init__(self, message: str, code: int = 402) -> None:
        super().__init__(message, code)

class SearchNotesParam(BaseModel):
    query: str = Field(description="搜索关键词")
    max_results: int = Field(description="最多返回条数",ge=1,le=20,default=5)

def search_notes(query:str,max_results:int=5):
    """返回包含关键词的笔记标题列表"""

    return [
        t
        for t in demo_notes if query and query in t['content']
    ]

class ReadNoteParam(BaseModel):
    note_id:int = Field(description="笔记id",gt=0)

def read_note(note_id:int):
    """根据note id获取笔记内容"""
    note = next(
        (n for n in demo_notes if n['id'] == note_id),
        None
    )

    if not note:
        raise NoteNotFoundError(f"笔记id：{note_id} 不存在！")

    return note



class SaveDraftParam(BaseModel):
    title:str = Field(description="标题",max_length=100,min_length=1)
    content:str = Field(description="内容",min_length=1)
    author:str = Field(description='作者',min_length=1)
    approve:bool = Field(description="是否允许调用", default=False)

def save_draft(title:str,content:str,author:str,approve:bool):
    """写入草稿"""
    global drafts_approval_required

    if drafts_approval_required and not approve:
        raise DraftNotApprovedError("不允许保存草稿！")

    print(f"⛔ 准备写入草稿：({title}, {content}, {author})")

class ApproveWritingParam(BaseModel):
    operation:str = Field(description="临时写入的内容")
    content:str = Field(description="内容",min_length=1)
    author:str = Field(description='作者',min_length=1)

def approve_writing(operation:str,content:str,author:str):
    """如果写入草稿失败，没有权限，临时允许写入内容"""
    global drafts_approval_required

    drafts_approval_required = False
    save_draft(operation,content,author,approve=True)
    drafts_approval_required = True

if __name__ == "__main__":
    print(search_notes("购物") )
    print(read_note(1))
    print(read_note(999))
    print(save_draft('a','b','c',approve=False))
    print(approve_writing('a','b','c'))
