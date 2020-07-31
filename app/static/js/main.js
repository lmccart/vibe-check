let image_base = 'http://167.172.202.13/images/';
let id = Number(window.location.pathname.substring(1));
let expression;
let photo_width, photo_height, photo_ratio;
let screen_width = window.innerWidth;
let mask_size = 3840;
let mask_zoom = 10.0;
let animation_duration = 5000;
let pause_duration = 3000;

$.get('/get_meta', data => {
  console.log(data)
  photo_width = data.photo_width;
  photo_height = data.photo_height;
  photo_ratio = window.innerHeight/photo_height;
  expression = data.expressions[id];

  $( '#label' ).css('color', data.colors[id]);
  $( '#expression' ).css('color', data.colors[id]);
  $( '#mask' ).attr('src', '/static/mask-'+expression+'.png');

  console.log(id, expression);
  // setInterval(update, 3000);
  update();
});

let update = () => {
  $.get('/static/data.json', data => {
    console.log(data[expression]);
    let expression_data = data[expression];
    $('#photo').attr('src', image_base+expression_data.photo_path);
    $('#expression').text(expression);

    let w = expression_data.rect[2] * photo_ratio;
    let h = expression_data.rect[3] * photo_ratio;
    let x = expression_data.rect[0] * photo_ratio;
    let y = expression_data.rect[1] * photo_ratio;
    
    // check which side of photo to start from
    let start_x = x < photo_width * photo_ratio * 0.5 ? -photo_width * photo_ratio + screen_width : 0;
    reset(x, y, start_x);
    zoomIn(x, y, start_x);
  });
};

// reset photo and mask
let reset = (x, y, start_x) => {
  $( '#photo' ).css('height', '100%');
  $( '#photo' ).css('left', start_x);
  $( '#mask' ).css('width', mask_size * mask_zoom);
  $( '#mask' ).css('height', mask_size * mask_zoom);
  $( '#mask' ).css('left', (x - mask_size * mask_zoom * 0.5));
  $( '#mask' ).css('top', (y - mask_size * mask_zoom * 0.5));
  $( '#mask' ).show();
};

// slide photo to final position
let slide = (x) => {
  let half = screen_width * 0.5;
  let target_x = half + (Math.random() - 0.5) * screen_width * 0.2;
  let left_diff = photo_width * photo_ratio - x;
  console.log(photo_width * photo_ratio, x, left_diff, half)
  if (target_x > x) target_x = x;
  else if (left_diff < half) target_x = target_x + (half - left_diff);
  let offset = target_x - x;
  $( '#photo' ).delay(pause_duration).animate({
    left: offset
  }, animation_duration, 'swing');
  return target_x;
}

// zoom into face
let zoomIn = (x, y, start_x) => {
  $('#label').css('display', 'inline-block');
  $('#label').addClass('blink');

  let target_x = slide(x);
  $( '#mask' ).delay(pause_duration).animate({
    width: mask_size,
    height: mask_size,
    left: target_x - mask_size * 0.5,
    top: y - mask_size * 0.5,
  }, animation_duration, 'swing', function () { zoomOut(x, y, start_x); });
  
  setTimeout(function() { 
    $('#label').removeClass('blink');
    $('#expression').css('display', 'inline-block');
  }, pause_duration + animation_duration);
}

// zoom out of face
let zoomOut = (x, y, start_x) => {
  $( '#photo' ).delay(pause_duration).animate({
    left: start_x
  }, animation_duration, 'swing');
  $( '#mask' ).delay(pause_duration).animate({
    width: mask_size * mask_zoom,
    height: mask_size * mask_zoom,
    left: (x - mask_size * mask_zoom * 0.5),
    top: (y - mask_size * mask_zoom * 0.5)
  }, animation_duration, 'swing', function () { zoomIn(x, y, start_x); });

  setTimeout(function() { 
    $('#label').hide();
    $('#expression').hide();
  }, pause_duration);
}