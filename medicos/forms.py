from django import forms
from .models import Medico, MedicoEspecialidad
from core.models import EspecialidadMedica


class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['numero_registro', 'nivel_academico', 'fecha_contratacion', 'estado', 'usuario']
        widgets = {
            'fecha_contratacion': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class EspecialidadMedicaForm(forms.ModelForm):
    class Meta:
        model = EspecialidadMedica
        fields = ['codigo', 'nombre', 'rama', 'duracion_anios', 'descripcion', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MedicoEspecialidadForm(forms.ModelForm):
    class Meta:
        model = MedicoEspecialidad
        fields = ['id_especialidad', 'nivel', 'fecha_certificacion', 'institucion']
        widgets = {
            'fecha_certificacion': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
