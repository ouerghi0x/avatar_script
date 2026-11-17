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
    is_prop: bool = False


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
    left_prop: str = "none",
    right_prop: str = "none",
    left_prop_scale: float = 1.0,
    right_prop_scale: float = 1.0,
    yaw: float = 0.0,
    pitch: float = 0.0,
    look_x: float = 0.0,
    look_y: float = 0.0,
) -> List[LayerState]:
    """Construct the ordered layer rig for a character at a specific state with 2.5D depth parallax."""
    expr_assets = resolve_expression_assets(expression, is_blinking=is_blinking)

    # 2.5D Parallax & Perspective depth factors:
    # yaw is horizontal rotation in degrees (-45 to +45 typical)
    # pitch is vertical rotation in degrees (-30 to +30 typical)
    # Normalized factors:
    ny = yaw / 45.0
    np = pitch / 30.0

    # Layer differential offsets:
    # Background (ears/head base) shifts slightly with head
    # Foreground features (eyes, mouth) shift significantly more
    head_dx = ny * 6.0
    head_dy = np * 4.0

    eyes_dx = ny * 24.0 + look_x
    eyes_dy = np * 14.0 + look_y
    # Perspective compression as head turns sideways
    eyes_scale_x = max(0.2, 1.0 - 0.20 * abs(ny))

    mouth_dx = ny * 18.0
    mouth_dy = np * 12.0
    mouth_scale_x = max(0.2, 1.0 - 0.16 * abs(ny))

    # Subtle counter-parallax for torso/arms
    body_dx = -ny * 2.0
    body_dy = np * 1.5

    layers = [
        LayerState(
            name="left_arm",
            asset_filename="left_arm.svg",
            z_order=10,
            x=-ny * 4.0,
            y=breathe_offset_y * 0.6,
            rotation=left_arm_rot,
            rotation_center=(95.0, 265.0),  # Pivot around shoulder socket
        ),
        LayerState(
            name="right_arm",
            asset_filename="right_arm.svg",
            z_order=15,
            x=-ny * 4.0,
            y=breathe_offset_y * 0.6,
            rotation=right_arm_rot,
            rotation_center=(305.0, 265.0),  # Pivot around shoulder socket
        ),
        LayerState(
            name="body",
            asset_filename="body.svg",
            z_order=20,
            x=body_dx,
            y=breathe_offset_y * 0.4 + body_dy,
            scale_y=breathe_scale_y,
        ),
        LayerState(
            name="head",
            asset_filename="head.svg",
            z_order=30,
            x=head_dx,
            y=breathe_offset_y + head_dy,
        ),
        LayerState(
            name="eyes",
            asset_filename=expr_assets.eyes_asset,
            z_order=40,
            x=eyes_dx,
            y=breathe_offset_y + eyes_dy,
            scale_x=eyes_scale_x,
        ),
        LayerState(
            name="mouth",
            asset_filename=expr_assets.mouth_asset,
            z_order=50,
            x=mouth_dx,
            y=breathe_offset_y + mouth_dy,
            scale_x=mouth_scale_x,
        ),
    ]

    # Attach left hand prop if equipped
    if left_prop and left_prop.lower() not in ("none", "off"):
        layers.append(
            LayerState(
                name="prop_left",
                asset_filename=f"{left_prop}.svg",
                z_order=12,
                x=-ny * 4.0,
                y=breathe_offset_y * 0.6,
                scale_x=left_prop_scale,
                scale_y=left_prop_scale,
                rotation=left_arm_rot,
                rotation_center=(95.0, 265.0),
                is_prop=True,
            )
        )

    # Attach right hand prop if equipped
    if right_prop and right_prop.lower() not in ("none", "off"):
        layers.append(
            LayerState(
                name="prop_right",
                asset_filename=f"{right_prop}.svg",
                z_order=60,  # Render on top of right arm/hand
                x=-ny * 4.0,
                y=breathe_offset_y * 0.6,
                scale_x=right_prop_scale,
                scale_y=right_prop_scale,
                rotation=right_arm_rot,
                rotation_center=(305.0, 265.0),
                is_prop=True,
            )
        )

    return sorted(layers, key=lambda l: l.z_order)
