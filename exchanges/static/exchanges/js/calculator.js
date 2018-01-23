//
//function profileCookieManager(){
//    var profileCookie = Cookies.get('profile_id');
//
//    if(profileCookie === undefined){
//        var profile_id = $('#profile_select').find('option').eq(0).attr('value');
//        setProfileCookie(profile_id);
//    }
//}
function setCookie(name, value, expires, path) {
  Cookies.set(name, value, { expires: expires, path: path });
  console.log(
    'Setting cookie: "' + name + '" (' + value + ') for ' + expires + ' days'
  );
}

function redirectTo(path) {
  console.log('Redirecting to: ' + path);
  window.location.replace(path);
}
//
// function selectPairFromCookie() {
//     const pair = Cookies.get('pair');
//     $('#selectPair').val(pair);
// }

$(document).ready(function() {
  const origin = document.location.origin;
  const page = '/calculator/';
  const mathAmountVolume = 'math/buy_amount_volume/';

  // selectPairFromCookie()

  $('#selectExchange').change(function() {
    const exchange = this.value;
    setCookie('exchange', exchange, 30, page);
    redirectTo(origin + page + exchange);
  });

  $('#selectPair').change(function() {
    const exchange = $('#selectExchange')
      .find('option:selected')
      .attr('value');
    setCookie('exchange', exchange, 30, page);

    const pair_name = $(this)
      .find('option:selected')
      .attr('name');
    setCookie('pair', this.value, 30, page + exchange);
    redirectTo(origin + page + exchange + '/' + pair_name);
  });

  $('#inputAmount').change(function() {
    const value = parseFloat($(this).val().replace(',','.'));
    if (isNaN(value) || value <= 0) {
      resetFields();
      return;
    }

    const pairId = $('#selectPair')
        .find('option:selected')
        .val();
    const side = 'right';

    getBuyAmountVolume(pairId, side, value)
      .then(function(data) {
        const volume = data.result.toFixed(8);
        $('#inputVolume')
          .val(volume)
          .attr('value', volume);
        updateFees();
      })
      .then(function(){
        const volume = parseFloat($('#inputVolume').val().replace(',','.'));
        return getSellResults(pairId, value, volume)
      })
      .catch(function(error) {
        resetFields();
        console.log('Request failed', error);
      });
  })

  $('#inputVolume').change(function() {
    const value = parseFloat($(this).val().replace(',','.'));
    if (isNaN(value) || value <= 0) {
      resetFields();
      return;
    }

    const pairId = $('#selectPair')
        .find('option:selected')
        .val();
    const side = 'left';

    getBuyAmountVolume(pairId, side, value)
      .then(function(data) {
        const amount = data.result.toFixed(2);
        $('#inputAmount')
          .val(amount)
          .attr('value', amount);
        updateFees();
      })
      .then(function(){
        const amount = parseFloat($('#inputAmount').val().replace(',','.'));
        return getSellResults(pairId, amount, value)
      })
      .then(function(result){
        console.log(result);
      })
      .catch(function(error) {
        resetFields();
        console.log('Request failed', error);
      });
  });

  function updateFees() {
    updateTakerFee();
  }

  function resetFields() {
    resetInputAmount();
    resetInputVolume();
    resetTakerFee();
  }

  function resetInputAmount(){
      $('#inputAmount').val('').attr('value', '');
  }

  function resetInputVolume(){
      $('#inputVolume').val('').attr('value', '');
  }

  function updateTakerFee(){
    const value = parseFloat($('#inputVolume').val());
    if (!isNaN(value) && value > 0)
      $('#takerFee').html(leftFormat.format((value*takerFee).toFixed(8)));
    else resetTakerFee();
  }

  function resetTakerFee(){
      $('#takerFee').html((takerFee*100).toFixed(2)+'%');
  }

  function json(response) {
    return response.json();
  }

  function getSellResults(pairId, amount, volume){
    const origin = document.location.origin;
    const page = '/calculator/';
    const mathSellResults = 'math/sell_results/';

    const data = new FormData();
    data.append('pair_id', pairId);
    data.append('amount', amount);
    data.append('volume', volume);

    return fetchPostApi(origin + page + mathSellResults, data)
  }

  function getBuyAmountVolume(pairId, side, value){
    const origin = document.location.origin;
    const page = '/calculator/';
    const mathAmountVolume = 'math/buy_amount_volume/';

    const data = new FormData();
    data.append('pair_id', pairId);
    data.append('side', side);
    data.append('value', value);

    return fetchPostApi(origin + page + mathAmountVolume, data)
  }

  function fetchPostApi(endpoint, data){
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();

    return fetch(endpoint, {
      method: 'post',
      headers: {
        'X-CSRFToken': csrf,
      },
      body: data,
      credentials: 'same-origin',
    }).then(json)
  }

  String.prototype.format = function() {
    a = this;
    for (k in arguments) {
      a = a.replace("{" + k + "}", arguments[k])
    }
    return a
  }
});
