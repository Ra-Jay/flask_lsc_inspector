# Backend Flask Continuous Deployment Script
# Pulling from https://github.com/Ra-Jay/flask_lsc_inspector `main` branch

# Set up variables
REMOTE_REPO="origin"
BRANCH="main"
REPO_NAME=$1
TAG=$2
NETWORK=$3
ENV=$4

# Check if argument exists
if [ -z "$REPO_NAME" ] || [ -z "$TAG" ] || [ -z "$NETWORK" ] || [ -z "$ENV" ]; then
    echo "Usage: $0 <repo_name> <tag> <network> <env>"
    exit 1
fi

# Function to check for new commits
check_commits() {
    git fetch $REMOTE_REPO $BRANCH &>/dev/null
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse $REMOTE_REPO/$BRANCH)
    BASE=$(git merge-base HEAD $REMOTE_REPO/$BRANCH)

    if [ $LOCAL != $REMOTE ] && [ $REMOTE != $BASE ]; then
        echo "New commits detected on $BRANCH. Pulling changes..."
        git pull $REMOTE_REPO $BRANCH &>/dev/null
        echo "Changes pulled successfully."
        echo "Saving container logs..."
        docker logs flask > flask.log
        echo "Stopping and removing the current container..."
        docker stop flask
        docker rm flask
        echo "Deleting old image..."
        docker rmi $REPO_NAME:$TAG
        echo "Building new image..."
        docker build -t $REPO_NAME:$TAG .
        echo "Pushing new image..."
        docker push $REPO_NAME:$TAG
        echo "Running new container..."
        docker run -d --restart=always --env-file $ENV --network=$NETWORK -p 5000:5000 --name flask $REPO_NAME:$TAG
    else
        dateofhead=$(git show --no-patch --format=%ci HEAD)
        echo "Fetched HEAD from $dateofhead. Already up to date."
    fi
}

# Main loop to continuously check for new commits
while true; do
    check_commits
    sleep 10800  # Check every 1 hour
done
