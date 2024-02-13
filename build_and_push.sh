# This script requires that the user must have a Docker Hub account and the Docker Desktop installed.
# Refer to this link to create a Docker Hub account: https://hub.docker.com/signup
# Refer to this link to install Docker Desktop: https://www.docker.com/products/docker-desktop
# Refer to this link to guide you on how to install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/


# REPO_AND_TAG is the name of the repository that you created in your Docker Hub 
# and the tag that you want to indicate.
REPO_AND_TAG=$1

# Check if all arguments are provided
if [ -z "$REPO_AND_TAG" ]; then
    echo "Usage: $0 <repo_and_tag>"
    exit 1
fi

# Build image with its tag.
docker build -t $REPO_AND_TAG .

# Push image to Docker Hub
docker push $REPO_AND_TAG