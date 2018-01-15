
//
//function profileCookieManager(){
//    var profileCookie = Cookies.get('profile_id');
//
//    if(profileCookie === undefined){
//        var profile_id = $('#profile_select').find('option').eq(0).attr('value');
//        setProfileCookie(profile_id);
//    }
//}
function setCookie(name, value, expires, path){
    Cookies.set(name, value, { expires: expires, path: path });
    console.log('Setting cookie: "'+name+'" (' + value + ') for ' + expires + ' days');
}

function redirectTo(path){
    console.log('Redirecting to: ' + path);
    window.location.replace(path);
}
//
// function selectPairFromCookie() {
//     const pair = Cookies.get('pair');
//     $('#selectPair').val(pair);
// }

$( document ).ready(function() {
    const origin = document.location.origin;
    const page = '/calculator/';

    // selectPairFromCookie()

    $('#selectExchange').change(function () {
        var exchange = this.value;
        setCookie('exchange', exchange, 30, page);
        redirectTo(origin+page+exchange);
    });

    $('#selectPair').change(function () {
        var exchange = $('#selectExchange').find('option:selected').attr('value');
        setCookie('exchange', exchange, 30, page);

        var pair_name = $(this).find('option:selected').attr('name');
        setCookie('pair', this.value, 30, page+exchange);
        redirectTo(origin+page+exchange+'/'+pair_name);
    });
});