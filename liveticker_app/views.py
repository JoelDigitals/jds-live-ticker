from django.shortcuts import render, redirect, get_object_or_404
from .models import LiveTicker
from .forms import LiveTickerForm, LiveTickerEventForm
from django.contrib.auth.decorators import login_required

@login_required
def liveticker_list(request):
    tickers = LiveTicker.objects.filter(owner=request.user)
    return render(request, 'liveticker/liveticker_list.html', {'tickers': tickers})

@login_required
def liveticker_detail(request, pk):
    ticker = get_object_or_404(LiveTicker, pk=pk, owner=request.user)
    events = ticker.events.all()

    if request.method == 'POST':
        event_form = LiveTickerEventForm(request.POST)
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.ticker = ticker
            event.save()
            return redirect('liveticker_detail', pk=ticker.pk)
    else:
        event_form = LiveTickerEventForm()

    return render(request, 'liveticker/liveticker_detail.html', {
        'ticker': ticker,
        'events': events,
        'event_form': event_form,
    })



@login_required
def liveticker_create(request):
    if request.method == 'POST':
        form = LiveTickerForm(request.POST)
        if form.is_valid():
            ticker = form.save(commit=False)
            ticker.owner = request.user
            ticker.save()
            return redirect('liveticker_list')
    else:
        form = LiveTickerForm()

    return render(request, 'liveticker/liveticker_create.html', {
        'form': form
    })

def liveticker_embed(request, pk):
    ticker = get_object_or_404(LiveTicker, pk=pk)
    style = request.GET.get('style', 'timeline')

    allowed_styles = ['timeline', 'cards', 'minimal']
    if style not in allowed_styles:
        style = 'timeline'

    return render(request, 'liveticker/embed.html', {
        'ticker': ticker,
        'style': style
    })

