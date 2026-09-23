from django import forms
from .models import ConsultaMedica, ConsultaSintoma, ConsultaDiagnostico
from core.models import Sintoma


class ConsultaMedicaForm(forms.ModelForm):
    class Meta:
        model = ConsultaMedica
        exclude = ['id_cita', 'fecha_consulta', 'creado_en', 'actualizado_en']
        widgets = {
            'examen_fisico': forms.Textarea(attrs={'rows': 3}),
            'tratamiento_prescrito': forms.Textarea(attrs={'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'rows': 2}),
            'proxima_cita': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ConsultaSintomaForm(forms.ModelForm):
    class Meta:
        model = ConsultaSintoma
        fields = ['id_sintoma', 'intensidad', 'duracion_dias', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ConsultaDiagnosticoForm(forms.ModelForm):
    class Meta:
        model = ConsultaDiagnostico
        fields = ['enfermedad', 'tipo', 'es_principal', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
