__author__ = 'Sereni'
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, MultiField, Fieldset, Field



class WordForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(WordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_tag = False  # do not enclose into <form>, because there will be many
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Field('lemma'),
            MultiField(  # these fieldsets should eventually get rendered as tabs in an appearing div
                'Grammatical tags',  # legend

                Fieldset(
                    'pos',
                    'number'
                )
            )
        )


    lemma = forms.CharField(label='Word', max_length=40)  # todo figure how to put numbers, and whether it needs a label at all

# todo when processing form output, you'll construct Penn Treebank tags out of pos and grammatical category input
# tell you what, make these codes human-readable, and convert to a specific tagset elsewhere
# what if we move from stanford to something else

# grammatical categories

    # hardcoded things
    number_choices = (
        ('sg', 'singular'),
        ('pl', 'plural')
    )

    pos_choices = (
        ('v', 'verb'),
        ('n', 'noun'),
        ('adj', 'adjective'),
        ('adv', 'adverb'),
        ('conj', 'conjunction'),
        ('det', 'determiner'),
        ('intj', 'interjection'),
        ('num', 'number'),
        ('prt', 'particle'),
        ('prn', 'pronoun'),  # let's stop for now, we'll add things on later
    )

    # field declarations
    pos = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=pos_choices)
    number = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=number_choices)