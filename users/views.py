from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import logout

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Willkommen {user.username}!")
            return redirect('liveticker_list')
        else:
            messages.error(request, "Benutzername oder Passwort ungültig.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Du wurdest erfolgreich ausgeloggt.")
    return redirect('login')


import secrets
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
import requests
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.translation import gettext as _


def sso_connect(request):
    """Startet SSO-Connect zu Joel Digitals"""
    print("\n" + "🟢" * 40)
    print("FUNCTION: sso_connect - AUFTRAGNETZ")
    print("🟢" * 40)
    
    # State generieren
    state = secrets.token_urlsafe(32)
    
    print(f"📝 State generiert: {state}")
    print(f"🌐 Session Key vorher: {request.session.session_key}")
    print(f"🌐 Session Keys vorher: {list(request.session.keys())}")
    
    # !!! WICHTIG: Session muss existieren BEVOR wir speichern !!!
    if not request.session.session_key:
        # Force Django to create a session
        request.session.create()
        print(f"✨ Neue Session erstellt: {request.session.session_key}")
    
    # State speichern
    request.session['sso_state'] = state
    request.session.modified = True
    request.session.save()
    
    print(f"💾 Session Key nachher: {request.session.session_key}")
    print(f"💾 State gespeichert: {request.session.get('sso_state')}")
    print(f"💾 Alle Session Keys: {list(request.session.keys())}")
    
    # Redirect URL
    sso_url = (
        f"{settings.SSO_PROVIDER_URL}/auth/sso/connect/"
        f"?client_id={settings.SSO_CLIENT_ID}"
        f"&redirect_uri={settings.SSO_CALLBACK_URL}"
        f"&state={state}"
    )
    
    print(f"↗️  Redirect zu: {sso_url}")
    print("🟢" * 40 + "\n")
    
    response = redirect(sso_url)
    
    # !!! WICHTIG: Session-Cookie muss gesetzt werden !!!
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=request.session.session_key,
        max_age=settings.SESSION_COOKIE_AGE,
        httponly=True,
        samesite='Lax',
    )
    
    return response

def sso_callback(request):
    """Empfängt SSO Token und erstellt/logged User ein"""
    print("\n" + "=" * 80)
    print("🔙 SSO CALLBACK - START")
    print("=" * 80)
    
    token = request.GET.get('token')
    state = request.GET.get('state')
    
    # State-Validierung
    stored_state = request.session.get('sso_state')
    
    if not stored_state and state:
        print("⚠️  WARNING: Session-State fehlt - akzeptiere State aus URL (DEV ONLY!)")
        request.session['sso_state'] = state
        stored_state = state
    
    if state != stored_state:
        print("❌ FEHLER: State Mismatch!")
        return redirect('/accounts/register/?error=invalid_state')
    
    print("✅ State validiert!")
    
    if not token:
        print("❌ FEHLER: Kein Token")
        return redirect('/accounts/register/?error=no_token')
    
    # Token validieren
    print(f"\n🔍 Validiere Token bei SSO Provider...")
    try:
        response = requests.post(
            f"{settings.SSO_PROVIDER_URL}/api/sso/validate/",
            data={
                'token': token,
                'client_id': settings.SSO_CLIENT_ID,
                'client_secret': settings.SSO_CLIENT_SECRET,
            },
            timeout=10,
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Token Validation fehlgeschlagen: {response.text}")
            return redirect('/accounts/register/?error=validation_failed')
        
        user_data = response.json()
        print(f"✅ Token validiert, User-Daten erhalten:")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Username: {user_data.get('username')}")
        print(f"   First Name: {user_data.get('first_name')}")
        print(f"   Last Name: {user_data.get('last_name')}")
        
        # Zuerst: Prüfe ob User mit dieser EMAIL bereits existiert
        try:
            user = User.objects.get(email=user_data['email'])
            print(f"✅ Bestehender User gefunden (via Email): {user.email}")
            
            # Update User-Daten falls sich was geändert hat
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.username = user_data.get('username', user.username)  # Update auch Username
            user.is_active = True
            user.email_confirmed = True
            user.save()
            print(f"📝 User-Daten aktualisiert")
            
        except User.DoesNotExist:
            # User existiert noch nicht → Erstellen
            print(f"📝 Erstelle neuen User...")
            
            # Generiere eindeutigen Username falls nötig
            base_username = user_data.get('username', user_data['email'].split('@')[0])
            username = base_username
            counter = 1
            
            # Prüfe ob Username bereits existiert
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                print(f"   Username '{base_username}' existiert bereits, versuche '{username}'")
            
            user = User.objects.create(
                email=user_data['email'],
                username=username,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                is_active=True,
                email_confirmed=True,
            )
            
            # Setze unbrauchbares Passwort (SSO-User)
            user.set_unusable_password()
            user.save()
            
            print(f"✨ Neuer SSO-User erstellt: {user.email} (Username: {user.username})")
        
        # User einloggen
        print(f"\n🔓 Logge User ein...")
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"✅ User eingeloggt: {user.email}")
        
        # Session cleanup
        if 'sso_state' in request.session:
            del request.session['sso_state']
        if 'sso_user_data' in request.session:
            del request.session['sso_user_data']
        
        print("\n" + "=" * 80)
        print("✅ SSO LOGIN - KOMPLETT ERFOLGREICH")
        print("=" * 80 + "\n")
        
        return redirect('/')  # Zur Startseite oder Dashboard
        
    except requests.RequestException as e:
        print(f"❌ SSO Request Error: {e}")
        print("=" * 80 + "\n")
        return redirect('/accounts/register/?error=connection_failed')
    
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.is_active = True
        user.save()
        messages.success(request, _("E-Mail bestätigt! Du kannst dich jetzt anmelden."))
        return redirect("login")
    else:
        messages.error(request, _("Der Verifizierungslink ist ungültig oder abgelaufen."))
        return redirect("home")


import requests
from django.contrib.auth import login
from django.shortcuts import redirect
from django.conf import settings
import secrets


def sso_login(request):
    """Startet SSO Login Flow"""
    print("\n" + "=" * 80)
    print("🚀 SSO LOGIN FLOW - START")
    print("=" * 80)
    
    # Zeige Request-Info
    print(f"\n🌐 Request Info:")
    print(f"   Path: {request.path}")
    print(f"   Method: {request.method}")
    print(f"   User: {request.user}")
    print(f"   Session Key (vorher): {request.session.session_key}")
    
    # State generieren
    state = secrets.token_urlsafe(32)
    
    print(f"\n📝 State generiert: {state}")
    
    # Session-Status VORHER
    print(f"\n💾 Session VORHER:")
    print(f"   Session Key: {request.session.session_key}")
    print(f"   Session Keys: {list(request.session.keys())}")
    print(f"   Session ist leer: {request.session.is_empty()}")
    
    # State speichern
    request.session['sso_state'] = state
    request.session.modified = True
    request.session.save()
    
    # Session-Status NACHHER
    print(f"\n💾 Session NACHHER:")
    print(f"   Session Key: {request.session.session_key}")
    print(f"   sso_state: {request.session.get('sso_state')}")
    print(f"   Alle Keys: {list(request.session.keys())}")
    print(f"   Session wurde gespeichert: {request.session.get('sso_state') == state}")
    
    # Redirect URL
    sso_url = (
        f"{settings.SSO_PROVIDER_URL}/auth/sso/connect/"
        f"?client_id={settings.SSO_CLIENT_ID}"
        f"&redirect_uri={settings.SSO_CALLBACK_URL}"
        f"&state={state}"
    )
    
    print(f"\n↗️  Redirect zu: {sso_url}")
    print("=" * 80 + "\n")
    
    return redirect(sso_url)
