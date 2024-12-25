from typing import Set

import numpy as np
import raylib as rl
from imgui_bundle import imgui
from imgui_bundle.python_backends.base_backend import BaseOpenGLRenderer

class RaylibGLRenderer(BaseOpenGLRenderer):

    def __init__(self, *args, **kwargs):
        self.wnd = kwargs.get("wnd")
        self._textures: Set[rl.Texture2D] = set()
        super().__init__()

        if hasattr(self, "wnd") and self.wnd:
            self.resize(*self.wnd.buffer_size)
        elif "display_size" in kwargs:
            self.io.display_size = kwargs.get("display_size")

    def _create_device_objects(self): ...


    def refresh_font_texture(self):
        font_matrix: np.ndarray = self.io.fonts.get_tex_data_as_rgba32()
        width: int = font_matrix.shape[1]
        height: int = font_matrix.shape[0]
        pixels: memoryview[int] = font_matrix.data

        if self._font_texture:
            rl.rlUnloadTexture(self._font_texture)

        pixels_ptr = rl.ffi.from_buffer(pixels)
        self._font_texture: int = rl.rlLoadTexture(
            pixels_ptr, width, height, rl.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8, 1
        )

        self.io.fonts.tex_id = self._font_texture
        self.io.fonts.clear_tex_data()

    def draw_triangle_vertex(self, idx_vert: imgui.ImDrawVert):

        color = idx_vert.col
        rl.rlColor4ub(
            (color >> 0) & 0xFF,
            (color >> 8) & 0xFF,
            (color >> 16) & 0xFF,
            (color >> 24) & 0xFF,
        )
        rl.rlTexCoord2f(idx_vert.uv.x, idx_vert.uv.y)
        rl.rlVertex2f(idx_vert.pos.x, idx_vert.pos.y)

    def render_draw_triangles(
        self,
        count: int,
        idx_offset: int,
        idx_buffer: list,
        idx_vert: imgui.ImDrawVert,
        texture_id: int,
    ):
        if count < 3:
            return

        rl.rlBegin(rl.RL_TRIANGLES)
        rl.rlSetTexture(texture_id or 0)
        # the complexity of this will increase with the complexity of the imgui draw data, so
        # maybe we should use a VBO with a VAO to store the data and render it in one go
        for i in range(0, count, 3):
            index_a = idx_buffer[idx_offset + i]
            index_b = idx_buffer[idx_offset + i + 1]
            index_c = idx_buffer[idx_offset + i + 2]

            vertex_a = idx_vert[index_a]
            vertex_b = idx_vert[index_b]
            vertex_c = idx_vert[index_c]
            self.draw_triangle_vertex(vertex_a)
            self.draw_triangle_vertex(vertex_b)
            self.draw_triangle_vertex(vertex_c)

        rl.rlEnd()

    def render(self, draw_data: imgui.ImDrawData):
        if not draw_data:
            return

        rl.rlDrawRenderBatchActive()
        rl.rlDisableBackfaceCulling()
        for n in range(draw_data.cmd_lists_count):
            cmd_list = draw_data.cmd_lists[n]
            for cmd in cmd_list.cmd_buffer:

                self.enable_scissor(
                    cmd.clip_rect.x - draw_data.display_pos.x,
                    cmd.clip_rect.y - draw_data.display_pos.y,
                    cmd.clip_rect.z - (cmd.clip_rect.x - draw_data.display_pos.x),
                    cmd.clip_rect.w - (cmd.clip_rect.y - draw_data.display_pos.y),
                )
                if cmd.user_callback_data:
                    cmd.user_callback_data(cmd_list, cmd)
                    continue

                self.render_draw_triangles(
                    cmd.elem_count,
                    cmd.idx_offset,
                    cmd_list.idx_buffer,
                    cmd_list.vtx_buffer,
                    cmd.texture_id,
                )
                rl.rlDrawRenderBatchActive()

        rl.rlSetTexture(0)
        rl.rlEnableBackfaceCulling()
        rl.rlDisableScissorTest()

    def _invalidate_device_objects(self):
        if self._font_texture:
            rl.rlUnloadTexture(self._font_texture)

        self.io.fonts.tex_id = 0
        self._font_texture = None

    def enable_scissor(self, x: float, y: float, width: float, height: float):
        rl.rlEnableScissorTest()
        io = self.io
        scale = io.display_framebuffer_scale
        rl.rlScissor(
            int(x * scale.x),
            int((io.display_size.y - int(y + height)) * scale.y),
            int(width * scale.x),
            int(height * scale.y),
        )
