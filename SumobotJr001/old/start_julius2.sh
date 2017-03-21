#USB ヘッドセット
#ALSADEV="plughw:0,0" ~/julius-4.3.1/julius/julius -C ~/julius_dic/command.jconf -module > /dev/null &

#マイク（プラグ）
ALSADEV="plughw:1,0" ~/julius-4.3.1/julius/julius -C ~/julius_dic/command2.jconf -module > /dev/null &

echo $!
sleep 3
