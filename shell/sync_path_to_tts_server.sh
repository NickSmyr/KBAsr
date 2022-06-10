# sync everything excluding things in .gitignore
# delete anything on target not in source
# include dotfiles and symlinks, also use compression
rsync --info=progress2 -azP --delete $1 nsmy@130.237.67.34:/home/nsmy/PersonalWorkspace/$1
