from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, post

from prodadvert.application.interactors.ai import TextGenerationInteractor
from prodadvert.controllers.http.openapi import success_spec, error_spec
from prodadvert.controllers.http.schemas import TextGenerationSchema, TextGenerationResponse


class AIController(Controller):
    path = "/ai"
    tags = ["AI"]

    @post(
        path="/generate-text",
        status_code=200,
        description=(
            "Generate text with AI.\n\n"
            "`topic` should be a short combination of words. "
            "Example: `gaming pc`, `grocery store`, etc. If "
            "you feel like adding more context, specify it "
            "in free form in `additional`."
        ),
        responses={
            200: success_spec("Text generated.", TextGenerationResponse),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def generate_text(
            self,
            data: TextGenerationSchema,
            interactor: FromDishka[TextGenerationInteractor]
    ) -> TextGenerationResponse:
        text = await interactor(data.topic, data.language, data.additional)
        return TextGenerationResponse(result=text)
