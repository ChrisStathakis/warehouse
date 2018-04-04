
$('.myForm').submit(function() {
    var c = confirm("Ειστε σίγουρος;");
    return c; //you can just return c because it will be true or false
});
$(function(){
    $('a.item').click(function(){
        $('.item').removeClass('active');
        $(this).addClass('active');
    });
    $('.message .close').on('click', function(){
    $(this).closest('.message')
        .transition('fade');
    });
    $('.ui.modal').modal('show');
    $('.ui.accordion').accordion();
    $('.ui.dropdown').dropdown();
    $('#select').dropdown();
    $('.vendor.modal').modal('setting', 'closable', false).modal('show');
    });
$(function(){
    $('.button').popup();
});
$(function(){
    $('a.item').popup();
});

$('.menu .item')
  .tab()
;
