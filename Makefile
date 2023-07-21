install:
	poetry env use 3.10
	poetry install

test-local:
	if [ ! -d ".venv" ]; then\
		make install;\
	fi
	poetry run pytest

build:
	docker build --platform linux/amd64 -t gcr.io/$(PROJECT_ID)/$(IMAGE):$(TAG) .

run-local:
	docker run -p 9000:9000 \
		-e PORT=9000 \
		-e LOCAL_HOST=$(LOCAL_HOST) \
		-e POSTMAN_HEADER=$(POSTMAN_HEADER) \
		gcr.io/$(PROJECT_ID)/$(IMAGE):$(TAG)

push:
	docker push gcr.io/$(PROJECT_ID)/$(IMAGE):$(TAG)

deploy:
	gcloud run deploy ${IMAGE} \
		--image=gcr.io/${PROJECT_ID}/${IMAGE}:${TAG} \
		--platform=managed \
		--region=asia-northeast1 \
		--timeout=60 \
		--concurrency=80 \
		--cpu=1 \
		--memory=128Mi \
		--max-instances=1  \
		--allow-unauthenticated \
		--set-env-vars=PREVIEW_FRONTEND_URL=${PREVIEW_FRONTEND_URL} \
		--set-env-vars=FRONTEND_URL_1=${FRONTEND_URL_1} \
		--set-env-vars=FRONTEND_URL_2=${FRONTEND_URL_2} \
		--set-env-vars=FRONTEND_URL_3=${FRONTEND_URL_3}
