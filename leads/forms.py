from django import forms


class TopicForm(forms.Form):
    topic = forms.CharField(
        max_length=255,
        label="Topic / Niche",
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. dental clinic Dhaka, freelance graphic designer Bangladesh",
                "class": "topic-input",
                "autofocus": True,
            }
        ),
        help_text="যত নির্দিষ্ট (specific) টপিক দিবে, রেজাল্ট তত ভালো হবে — শুধু 'business' না লিখে 'furniture shop Chittagong' টাইপ কিছু লিখো।",
    )
