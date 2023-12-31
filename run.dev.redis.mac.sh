# `-r` to stop, rebuild and restart containers
# `-h` for help

while getopts :r flag
do
    case "${flag}" in
        r)
            printf "Stop, redbuild and restart DEV (MAC) containers...\n";
            docker-compose -f docker-compose.dev.redis_only.mac.yml --env-file .env.dev down -v
            docker-compose -f docker-compose.dev.redis_only.mac.yml --env-file .env.dev up -d --build
        ;;
        *)
            printf "Usage: run.dev.sh [-r] [-h]\n";
            printf "Options:\n"
            printf "  -r\tStop, redbuild and restart DEV (MAC) containers\n";
        ;;
    esac
done

# If no options are passed, build and start DEV containers
if (( $OPTIND == 1 )); then
    printf "Build and start DEV (MAC) containers...\n";
    docker-compose -f docker-compose.dev.redis_only.mac.yml --env-file .env.dev up -d --build
fi
