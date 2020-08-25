# rsync --progress -rav hek:~/Documents/vibe-check/app/images .
ssh hek "mongodump -d vibecheck --collection raw --archive" | \
    mongorestore --nsInclude vibecheck.raw --archive