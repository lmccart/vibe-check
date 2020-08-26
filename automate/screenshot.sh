mkdir -p screenshot
cd screenshot
{
    DISPLAY=:0.0 scrot 0.jpg -t 50 &
    DISPLAY=:0.1 scrot 1.jpg -t 50 &
}
wait