"""Typed Abstract Syntax Tree (AST) nodes for AvatarScript."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class SourceLocation:
    line: int
    column: int


@dataclass
class ASTNode:
    loc: SourceLocation


@dataclass
class ExpressionNode(ASTNode):
    expression: str


@dataclass
class AnimationNode(ASTNode):
    kind: str  # 'shake', 'bounce', 'move', 'rotate', 'fade', 'scale', 'aura', etc.
    duration: Optional[float] = None
    easing: str = "ease_in_out"
    intensity: Optional[float] = None
    params: Dict[str, Any] = field(default_factory=dict)
    scalar_target: Optional[Union[float, str]] = None


@dataclass
class HoldNode(ASTNode):
    item: str
    hand: str = "right"  # 'left' or 'right'


@dataclass
class AvatarPropertyNode(ASTNode):
    name: str
    value: Union[str, float, Tuple[float, float], Tuple[str, str]]


ActionNode = Union[ExpressionNode, AnimationNode, AvatarPropertyNode]


@dataclass
class TimelineBlockNode(ASTNode):
    timestamp: float
    actions: List[ActionNode] = field(default_factory=list)


@dataclass
class IdleBlockNode(ASTNode):
    breathe: bool = False
    blink_interval: Optional[float] = None


@dataclass
class AvatarNode(ASTNode):
    identifier: str
    properties: List[AvatarPropertyNode] = field(default_factory=list)
    idle: Optional[IdleBlockNode] = None
    timeline_blocks: List[TimelineBlockNode] = field(default_factory=list)


@dataclass
class ScenePropertyNode(ASTNode):
    name: str
    value: Union[str, int, float, Tuple[int, int]]


@dataclass
class SceneNode(ASTNode):
    name: str
    properties: List[ScenePropertyNode] = field(default_factory=list)
    avatars: List[AvatarNode] = field(default_factory=list)
