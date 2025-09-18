#!/bin/sh
# note: this provides the Docker socket to the image and is NOT intended as a security container
if [ ! -f ".env" ]; then
    touch ".env"
fi
docker run -i \
       --platform linux/amd64 \
       --volume /var/run/docker.sock:/var/run/docker.sock \
       --volume "$PWD/"logs:/app/logs \
       --mount type=bind,src="$PWD/".env,dst=/app/.env,ro \
       ${MY_DATA:+--mount type=bind,src=$MY_DATA,dst=/app/my_data} \
       ${MY_TASKFLOWS:+--mount type=bind,src=$MY_TASKFLOWS,dst=/app/taskflows/my_taskflows,ro} \
       ${MY_TOOLBOXES:+--mount type=bind,src=$MY_TOOLBOXES,dst=/app/toolboxes/my_toolboxes,ro} \
       ${MY_PROMPTS:+--mount type=bind,src=$MY_PROMPTS,dst=/app/prompts/my_prompts,ro} \
       ${MY_PERSONALITIES:+--mount type=bind,src=$MY_PERSONALITIES,dst=/app/personalities/my_personalities,ro} \
       "ghcr.io/githubsecuritylab/seclab-taskflow-agent" "$@"
