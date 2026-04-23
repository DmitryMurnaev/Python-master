"""
app/schemas/__init__.py
======================
Все Pydantic схемы приложения.

Импортируем для удобства:
    from app.schemas import UserCreate, UserResponse, BlockResponse, etc.
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserProfile,
    Token,
    TokenData,
)
from app.schemas.learning import (
    BlockBase,
    BlockCreate,
    BlockResponse,
    BlockDetail,
    LessonBase,
    LessonCreate,
    LessonResponse,
    LessonDetail,
    QuizBase,
    QuizCreate,
    QuizQuestion,
    QuizResponse,
    QuizSubmission,
    QuizResultResponse,
    TaskBase,
    TaskCreate,
    TaskResponse,
    TaskDetail,
    TaskSubmissionCode,
    TaskSubmissionResult,
)
from app.schemas.progress import (
    ProgressStats,
    BlockProgress,
    AchievementBase,
    AchievementResponse,
    DailyChallengeResponse,
    LeaderboardEntry,
    ActivityDay,
)
from app.schemas.flashcard import (
    FlashCardBase,
    FlashCardCreate,
    FlashCardUpdate,
    FlashCardResponse,
    FlashCardReview,
    FlashCardStudySession,
    FlashCardStats,
)
from app.schemas.interpreter import (
    InterpreterRequest,
    InterpreterResponse,
    InterpreterError,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "Token",
    "TokenData",
    # Learning schemas
    "BlockBase",
    "BlockCreate",
    "BlockResponse",
    "BlockDetail",
    "LessonBase",
    "LessonCreate",
    "LessonResponse",
    "LessonDetail",
    "QuizBase",
    "QuizCreate",
    "QuizQuestion",
    "QuizResponse",
    "QuizSubmission",
    "QuizResultResponse",
    "TaskBase",
    "TaskCreate",
    "TaskResponse",
    "TaskDetail",
    "TaskSubmissionCode",
    "TaskSubmissionResult",
    # Progress schemas
    "ProgressStats",
    "BlockProgress",
    "AchievementBase",
    "AchievementResponse",
    "DailyChallengeResponse",
    "LeaderboardEntry",
    "ActivityDay",
    # Flashcard schemas
    "FlashCardBase",
    "FlashCardCreate",
    "FlashCardUpdate",
    "FlashCardResponse",
    "FlashCardReview",
    "FlashCardStudySession",
    "FlashCardStats",
    # Interpreter schemas
    "InterpreterRequest",
    "InterpreterResponse",
    "InterpreterError",
]