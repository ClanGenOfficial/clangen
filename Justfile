optimize-images:
    rg --files -g '*.png' -g '*.PNG' -0 | xargs -0 -r oxipng -o 4 --strip safe --nc --
