#!/bin/bash
pipeline_name='forecasting_example'
component_name='linear_regression_training'
docker_container=$DOCKER_CONTAINER_REGISTRY_BASE_URL
image_name=${docker_container}/${pipeline_name}/${component_name}
image_tag=$TAG
full_image_name=${image_name}:${image_tag}

docker build -t ${full_image_name} .
docker push "$full_image_name"

# Output the strict image name (which contains the sha256 image digest)
docker inspect --format="{{index .RepoDigests 0}}" "${full_image_name}"

