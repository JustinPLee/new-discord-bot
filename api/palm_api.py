import google.generativeai as palm

from secret import PALM_KEY

from log import log

palm.configure(api_key=PALM_KEY)

class PalmApi:

    source = "PaLM"
    # text-bison
    model = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods][0].name

    @classmethod
    def extract(cls, **kwargs) -> str:
        prompt = kwargs['prompt']
        try:
            # default settings
            result = palm.generate_text(
                model=cls.model,
                prompt=prompt,
                temperature=0.5,
                max_output_tokens=800
            )
        except Exception as err:
            log(err)
            return {}
        return {
            'result': result.result,
            'source': cls.source
        }