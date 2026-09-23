from django import forms
from .models import Persona, PersonaAlergia, PersonaContacto, PersonaDiscapacidad, Nombre
from core.models import TipoDocumento, TipoSangre, TipoAlergia, TipoDiscapacidad, TipoContacto, Parroquia, Municipio, Etnia, Sector, Calle


class PersonaForm(forms.ModelForm):
    primer_nombre = forms.CharField(max_length=52, label='Primer Nombre')
    apellido = forms.CharField(max_length=52, label='Apellido')
    id_municipio = forms.ModelChoiceField(
        queryset=Municipio.objects.all(), label='Municipio', required=False
    )
    # Etnia: We'll show this as a choice field and handle PersonaEtnia in save
    id_etnia = forms.ModelChoiceField(
        queryset=Etnia.objects.all(), label='Etnia', required=False
    )
    # Discapacidades: multiple choice
    discapacidades_list = forms.ModelMultipleChoiceField(
        queryset=TipoDiscapacidad.objects.all(), label='Discapacidades',
        widget=forms.CheckboxSelectMultiple, required=False
    )

    # Alergias (Opcional al registrar)
    alergia_tipo = forms.ModelChoiceField(
        queryset=TipoAlergia.objects.all(), label='Tipo de Alergia', required=False
    )
    alergia_nombre = forms.CharField(max_length=200, label='Nombre de la alergia', required=False)
    alergia_severidad = forms.ChoiceField(
        choices=[('', '---------'), ('LEVE', 'Leve'), ('MODERADA', 'Moderada'), ('GRAVE', 'Grave')],
        label='Severidad', required=False
    )

    class Meta:
        model = Persona
        fields = [
            'id_tipo_documento', 'numero_documento', 'fecha_nacimiento', 'sexo',
            'id_tipo_sangre', 'telefono', 'parroquia', 'id_sector', 'id_calle',
            'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
            'privado_de_libertad'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        if instance:
            initial['primer_nombre'] = instance.id_nombre.nombre if instance.id_nombre else ''
            initial['apellido'] = instance.id_apellido.nombre if instance.id_apellido else ''
            # initial for etnia
            if hasattr(instance, 'etnia'):
                initial['id_etnia'] = instance.etnia.id_etnia
            # initial for disabilities
            initial['discapacidades_list'] = [d.id_tipo_discapacidad for d in instance.discapacidades.all()]
            # initial for municipio
            if instance.parroquia:
                initial['id_municipio'] = instance.parroquia.municipio
        
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        # Exclude explicit FK fields from fields if we handle them specially
        # But here we want them in the form for select inputs
        for field_name, field in self.fields.items():
            classes = ['form-control']
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                classes = []
            elif field_name == 'privado_de_libertad':
                classes = ['form-check-input']
            
            if classes:
                field.widget.attrs['class'] = ' '.join(classes)

    def is_valid(self):
        valid = super().is_valid()
        for field in self.errors:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] += ' is-invalid'
        return valid

    def save(self, commit=True):
        persona = super().save(commit=False)
        primer_nombre = self.cleaned_data.get('primer_nombre', '').strip()
        apellido = self.cleaned_data.get('apellido', '').strip()

        nombre_obj, _ = Nombre.objects.get_or_create(
            nombre=primer_nombre, tipos_nombre='nombre'
        )
        apellido_obj, _ = Nombre.objects.get_or_create(
            nombre=apellido, tipos_nombre='apellido'
        )
        persona.id_nombre = nombre_obj
        persona.id_apellido = apellido_obj
        
        if commit:
            persona.save()
            # Save Etnia
            etnia = self.cleaned_data.get('id_etnia')
            from .models import PersonaEtnia, PersonaDiscapacidad, PersonaAlergia
            if etnia:
                PersonaEtnia.objects.update_or_create(id_persona=persona, defaults={'id_etnia': etnia})
            
            # Save Discapacidades (Reset and add)
            persona.discapacidades.all().delete()
            for disc_tipo in self.cleaned_data.get('discapacidades_list', []):
                PersonaDiscapacidad.objects.create(id_persona=persona, id_tipo_discapacidad=disc_tipo, grado='NO_ESPECIFICADO')
                
            # Alergia (if any details are given)
            al_tipo = self.cleaned_data.get('alergia_tipo')
            al_nom = self.cleaned_data.get('alergia_nombre')
            al_sev = self.cleaned_data.get('alergia_severidad')
            if al_tipo and al_nom:
                # We can add this simply or update existing ones. Just adding is fine for formulation.
                # If they want more, they use the detailed allergies section later.
                PersonaAlergia.objects.create(
                    id_persona=persona,
                    id_tipo_alergia=al_tipo,
                    nombre_alergia=al_nom,
                    severidad=al_sev or 'LEVE'
                )

        return persona


class PersonaAlergiaForm(forms.ModelForm):
    class Meta:
        model = PersonaAlergia
        fields = ['id_tipo_alergia', 'nombre_alergia', 'severidad', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PersonaContactoForm(forms.ModelForm):
    class Meta:
        model = PersonaContacto
        fields = ['id_tipo_contacto', 'valor', 'es_principal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
