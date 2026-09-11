shader_type canvas_item;
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform float strength = 0.0;
uniform float flash = 0.0;
void fragment() {
    vec2 uv=SCREEN_UV;
    vec2 delta=uv-vec2(0.5);
    uv+=normalize(delta+vec2(0.001))*sin(length(delta)*45.0-TIME*18.0)*strength*0.003;
    COLOR=vec4(texture(screen_texture,uv).rgb+vec3(flash),1.0);
}
