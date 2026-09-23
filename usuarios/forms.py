from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Usuario'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Contraseña'
        })


class UsuarioForm(forms.ModelForm):
    """Formulario de CREACIÓN — contraseña obligatoria."""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'telefono']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'rol':        forms.Select(attrs={'class': 'form-control'}),
            'telefono':   forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.hide_medico = kwargs.pop('hide_medico', True)
        super().__init__(*args, **kwargs)
        if self.hide_medico and 'rol' in self.fields:
            self.fields['rol'].choices = [c for c in self.fields['rol'].choices if c[0] != 'MEDICO']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UsuarioEditForm(forms.ModelForm):
    """Formulario de EDICIÓN — datos generales sin contraseña."""
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'telefono', 'activo']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'rol':        forms.Select(attrs={'class': 'form-control'}),
            'telefono':   forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.hide_medico = kwargs.pop('hide_medico', True)
        super().__init__(*args, **kwargs)
        if self.hide_medico and 'rol' in self.fields:
            if self.instance and self.instance.rol == 'MEDICO':
                pass
            else:
                self.fields['rol'].choices = [c for c in self.fields['rol'].choices if c[0] != 'MEDICO']


class UsuarioPasswordForm(forms.Form):
    """Formulario independiente para cambiar contraseña de un usuario."""
    password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'id': 'id_new_password1',
        })
    )
    password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'id': 'id_new_password2',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        if p1 and len(p1) < 8:
            self.add_error('password1', 'La contraseña debe tener al menos 8 caracteres.')
        return cleaned_data
