let image_base = 'http://167.172.202.13/images/';
let id = Number(window.location.pathname.substring(1));
let expression;
let photo_width, photo_height, photo_ratio;

$.get('/get_meta', data => {
  console.log(data)
  photo_width = data.photo_width;
  photo_height = data.photo_height;
  photo_ratio = window.innerWidth/photo_width;
  expression = data.expressions[id];
  console.log(id, expression);
  // setInterval(update, 3000);
  update();

  zoomIn();
});

let update = () => {
  $.get('/static/data.json', data => {
    console.log(data[expression]);
    let expression_data = data[expression];
    $('#photo').attr('src', image_base+expression_data.photo_path);
    $('#expression').text(expression);

    let w = expression_data.rect[2] * photo_ratio;
    let h = expression_data.rect[3] * photo_ratio;
    $('#rect').css('left', expression_data.rect[0] * photo_ratio - w/2);
    $('#rect').css('top', expression_data.rect[1] * photo_ratio - h/2);
    $('#rect').css('width', w);
    $('#rect').css('height', h);
  });
};

let zoomIn = () => {
  $( '#mask' ).css('width', '200%');
  $( '#mask' ).css('left', '-25%');
  $( '#mask' ).css('top', '-25%');
  $('#mask').show();
  $( '#mask' ).animate({
    width: '100%',
    left: '0',
    top: '0',
  }, 5000, 'swing', zoomOut);
}

let zoomOut = () => {
  $( '#mask' ).css('width', '100%');
  $( '#mask' ).css('left', '0');
  $( '#mask' ).css('top', '0');
  $('#mask').show();
  $( '#mask' ).animate({
    width: '200%',
    left: '-25%',
    top: '-25%',
  }, 5000, 'linear', zoomIn);
}