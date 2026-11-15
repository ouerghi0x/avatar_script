"""Layer-based 2D Avatar model and deterministic state representation."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from avatarscript.runtime.expressions import resolve_expression_assets
from avatarscript.renderer.aura_renderer import AuraState


@dataclass
class LayerState:
    name: str
    asset_filename: str
    z_order: int
    x: float = 0.0
    y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0
    rotation_center: Tuple[float, float] = (200.0, 250.0)
    visible: bool = True
    opacity: float = 1.0


@dataclass
class AvatarState:
    """Complete deterministic state of an avatar at a given timestamp t."""
    identifier: str
    character: str
    x: float
    y: float
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    expression: str = "neutral"
    is_blinking: bool = False
    layers: List[LayerState] = field(default_factory=list)
    aura: AuraState = field(default_factory=AuraState)


def resolve_named_position(pos_name: str, canvas_width: int, canvas_height: int) -> Tuple[float, float]:
    """Resolve preset positions ('left', 'center', 'right') to pixel coordinates."""
    cy = canvas_height * 0.60
    if pos_name == "left":
        return (canvas_width * 0.25, cy)
    if pos_name == "right":
        return (canvas_width * 0.75, cy)
    return (canvas_width * 0.50, cy)


def build_default_layers(
    expression: str = "neutral",
    is_blinking: bool = False,
    breathe_offset_y: float = 0.0,
    breathe_scale_y: float = 1.0,
    left_arm_rot: float = 0.0,
    right_arm_rot: float = 0.0,
) -> List[LayerState]:
    """Construct the ordered 6-layer rig for a character at a specific state."""
    expr_assets = resolve_expression_assets(expression, is_blinking=is_blinking)
    layers = [
        LayerState(
            name="left_arm",
            asset_filename="left_arm.svg",
            z_order=10,
            y=breathe_offset_y * 0.6,
            rotation=left_arm_rot,
            rotation_center=(95.0, 265.0),  # Pivot around shoulder socket
        ),
        LayerState(
            name="right_arm",
            asset_filename="right_arm.svg",
            z_order=15,
            y=breathe_offset_y * 0.6,
            rotation=right_arm_rot,
            rotation_center=(305.0, 265.0),  # Pivot around shoulder socket
        ),
        LayerState(name="body", asset_filename="body.svg", z_order=20, y=breathe_offset_y * 0.4, scale_y=breathe_scale_y),
        LayerState(name="head", asset_filename="head.svg", z_order=30, y=breathe_offset_y),
        LayerState(name="eyes", asset_filename=expr_assets.eyes_asset, z_order=40, y=breathe_offset_y),
        LayerState(name="mouth", asset_filename=expr_assets.mouth_asset, z_order=50, y=breathe_offset_y),
    ]
    return sorted(layers, key=lambda l: l.z_order)
