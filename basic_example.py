"""

raylib [core] example - Basic window with imgui

"""
import pyray


from imgui_bundle import imgui

from imgui_integration import init_imgui
# Initialization
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

pyray.set_config_flags(pyray.ConfigFlags.FLAG_WINDOW_RESIZABLE)
pyray.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, 'raylib example - basic window with imgui')
pyray.set_target_fps(60)
imgui_backend = init_imgui()

# variables
counter = 0
# init imgui

# Main game loop
while not pyray.window_should_close():  # Detect window close button or ESC key
    # Update
    # TODO: Update your variables here
    imgui_backend.process_inputs()

    # Draw
    pyray.begin_drawing()

    pyray.clear_background(pyray.RAYWHITE)

    pyray.draw_text(
        'This is a raylib + imgui integration example!', 190, 200, 20, pyray.LIGHTGRAY)
    pyray.draw_text(f'Counter: {counter}', 300, 250, 20, pyray.LIGHTGRAY)

    # We need to draw the current batch to prevent imgui from rendering below raylib elements
    pyray.rl_draw_render_batch_active()
    # Draw imgui
    imgui.new_frame()
    imgui.begin("Hello, world!")
    imgui.text("This is some useful text. :p")
    if imgui.button("Click me!"):
        counter += 1
    imgui.end()

    # Show the demo window
    imgui.show_demo_window()
    imgui.render()

    # also need to pass the draw data to the backend
    # heres the magic, we could use rgl instead of moderngl as the renderer backend
    imgui_backend.render(imgui.get_draw_data())
    pyray.end_drawing() # and swap buffers


# De-Initialization
imgui_backend.shutdown()
pyray.close_window()  # Close window and OpenGL context
