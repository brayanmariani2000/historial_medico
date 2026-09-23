from django import forms
from .models import Cita
from core.models import EstadoCita, TipoConsulta, EspecialidadMedica
from pacientes.models import Persona
from medicos.models import Medico

class CitaForm(forms.ModelForm):
    id_especialidad = forms.ModelChoiceField(
        queryset=EspecialidadMedica.objects.filter(activo='SI'), 
        label='Área de Consulta (Especialidad)',
        required=False
    )

    class Meta:
        model = Cita
        fields = [
            'id_persona', 'id_especialidad', 'id_medico', 'id_tipo_consulta',
            'fecha_cita', 'motivo_consulta', 'observaciones', 'id_triage'
        ]
        widgets = {
            'fecha_cita': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_persona'].queryset = Persona.objects.filter(activo=True)
        self.fields['id_medico'].queryset = Medico.objects.filter(estado='ACTIVO')
        self.fields['id_triage'].required = False
        for field_name, field in self.fields.items():
            classes = ['form-control']
            field.widget.attrs['class'] = ' '.join(classes)

    def is_valid(self):
        valid = super().is_valid()
        for field in self.errors:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] += ' is-invalid'
        return valid

class CitaEstadoForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['id_estado_cita', 'motivo_cancelacion']
        widgets = {
            'motivo_cancelacion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
