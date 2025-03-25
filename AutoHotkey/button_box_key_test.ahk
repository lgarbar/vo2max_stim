; Left Mouse Button -> "a" key
LButton::
{
    Send "a"
}

; Right Mouse Button -> "d" key
RButton::
{
    if (GetKeyState("RButton", "P"))
    {
        Send "d"
    }
    return
}

; Middle Mouse Button -> "Space" key
MButton::
{
    Send "{Space}"
}
