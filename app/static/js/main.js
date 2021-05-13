let image_base = './images/';
let id = Number(window.location.pathname.substring(1));
let expression, label;
let photo_width, photo_height, photo_ratio;
let screen_width = window.innerWidth;
let screen_height = window.innerHeight;
let mask_size = 3840;
let mask_zoom = 10.0;

let rush_debug = false;
let speed = 1;
let animation_duration = 3000 / speed;
let zoomed_in_pause_duration = 4000 / speed;
let zoomed_out_pause_duration = 5000 / speed;
let mask_zoom_duration = 1000 / speed;
let stored_face_x, stored_face_y, stored_photo_out_x, stored_photo_in_x, stored_mask_in_x;
let blink_interval;
let screen_off = (id+1) * 100 / speed;

let timeline;


let getConfig = () => {
  $.get('/static/config.json', data => {
    console.log(data)
    photo_ratio = screen_height/data.photo_height;
    photo_width = data.photo_width * photo_ratio;
    photo_height = data.photo_height * photo_ratio;
    expression = data.expressions[id].expression;
    label = data.expressions[id].label;
  
    $( '#label' ).css('color', data.expressions[id].color);
    $( '#expression' ).css('color', data.expressions[id].color);
    $( '#mask' ).attr('src', '/static/mask-'+expression+'.png');
    
    update(true);
  });  
}
getConfig();

let update = (ready) => {
  let now = new Date().getTime();
  $.get('/static/data.json?'+now, data => {
    let expression_data = data[expression];
    let url = image_base+expression_data.photo_path;
    if (url !== $('#photo').attr('src')) {
      $('#photo').attr('src', url);
    }
    $('#expression').text(label);

    let face_w = expression_data.rect[2] * photo_ratio;
    let face_h = expression_data.rect[3] * photo_ratio;
    stored_face_x = expression_data.rect[0] * photo_ratio;
    stored_face_y = expression_data.rect[1] * photo_ratio;
    
    // check which side of photo to start from
    // calculate stored_photo_out_x
    stored_photo_out_x = stored_face_x < photo_width * 0.5 ? -photo_width + screen_width : 0;

    // calculate stored_photo_in_x, stored_mask_in_x
    let half = screen_width * 0.5;
    stored_mask_in_x = half + (Math.random() - 0.5) * screen_width * 0.2;
    let left_diff = photo_width - stored_face_x;
    if (stored_mask_in_x > stored_face_x) stored_mask_in_x = stored_face_x;
    else if (left_diff < half) stored_mask_in_x = stored_mask_in_x + (half - left_diff);
    let offset = stored_mask_in_x - stored_face_x;
    offset = Math.max(offset, screen_width - photo_width);
    offset = Math.min(offset, 0);
    stored_photo_in_x = offset

    if (ready) start();
  });
};

let start = () => {
  
  reset();

  let totalTime = zoomed_in_pause_duration + zoomed_out_pause_duration + 2 * animation_duration;
  let millis = new Date().getTime();
  let rem = millis % totalTime;
  let diff = totalTime - rem;
  if (diff < 1000) diff += totalTime;
  if (rush_debug) diff = 500;

  let t = 0;

  timeline = new Timeline({ loop: true, duration: totalTime, interval: 100 });
  timeline.add({ time: t, event: slideIn});
  t += animation_duration - mask_zoom_duration + screen_off;
  timeline.add({ time: t, event: zoomIn });
  t += mask_zoom_duration;
  timeline.add({ time: t, event: showLabel });
  t += zoomed_in_pause_duration - screen_off;
  timeline.add({ time: t, event: hideLabel });
  timeline.add({ time: t, event: slideAndZoomOut});
  t += animation_duration + screen_off;
  timeline.add({ time: t, event: blinkLabel });
  timeline.add({ time: t, event: update });

  t += zoomed_out_pause_duration - screen_off;

  timeline.setDuration(t);

  setTimeout(function() {
    blink(true);
    timeline.start();
  }, diff);
  console.log(diff);
}

let reset = () => {
  $( '#photo' ).css('height', '100%');
  $( '#photo' ).css('transform', 'translate(0, 0)');
  $( '#mask' ).css('width', mask_size);
  $( '#mask' ).css('height', mask_size);
  $( '#mask' ).css('transform', `translate(${stored_face_x - mask_size * 0.5}px, ${stored_face_y - mask_size * 0.5}px) scale(${mask_zoom})`);
  $( '#label').hide();

  $( '#mask' ).show();
  $( '#photo').stop();
  $( '#mask').stop();
  $( '#label').stop();
  $( '#expression').stop();
};


let slideIn = () => {
  $('#photo').css('transform', `translate(${stored_photo_in_x}px, 0)`);
}

let zoomIn = () => {
  $( '#mask' ).css('transform', `translate(${stored_mask_in_x - mask_size * 0.5}px, ${stored_face_y - mask_size * 0.5}px) scale(1)`);
}

let slideAndZoomOut = () => {
  $('#photo').css('transform', `translate(${stored_photo_out_x}px, 0)`);
  $('#mask').css('transform', `translate(${stored_face_x - mask_size * 0.5}px, ${stored_face_y - mask_size * 0.5}px) scale(${mask_zoom})`);
}


let blinkLabel = () => {
  blink(true);
  $('#label').hide();
};

let showLabel = () => {
  blink(false);
  $('#label').show();
  $('#expression').css('margin-left', ((Math.random() > 0.5 ? 1 : -1) * 1.6) + 'em');
  $('#expression').css('opacity', 1);
};

let hideLabel = () => {
  blink(false);
  $('#label').hide();
  $('#expression').css('margin-left', 0);
  $('#expression').css('opacity', 0);
};

let blink = (val) => {
  if (val) {
    $('#expression').addClass('blink');
  } else $('#expression').removeClass('blink');
};






class Timeline {

  constructor(opts) {
    this.timeline = {};
    this.completed_events = {};
    this.interval = opts.interval;
    this.loop = opts.loop;
    this.duration = opts.duration;
    this.status = 'stopped';
    this.startTime = null;
  }

  add(opts) {
    let id = (Date.now().toString(36) + Math.random().toString(36).substr(2, 5)).toUpperCase();
    this.timeline[id] = opts;
  }

  clear() {
    this.timeline = {};
    this.completed_events = {};
    this.startTime = null;
  }

  setDuration(duration) {
    this.duration = duration;
  }

  reset() {
    this.completed_events = {};
    this.startTime = Date.now();
  }

  stop() {
    this.status = 'stopped';
  }

  _play_uncompleted() {
    let curtime = Date.now();

    for (const k in this.timeline) {
      if ((curtime >= Number(this.timeline[k].time) + this.startTime) && !(k in this.completed_events)) {
        this.timeline[k].event();
        this.completed_events[k] = true;
      } 
    }
  }

  update() {
    this._play_uncompleted();
  }

  start(opts) {
    var self = this;

    this.reset();
    this.status = 'playing';

    var loopUpdate = function() {

      setTimeout(function() {
        if (self.status === 'stopped') {
          return; 
        } 
        self.update();

        let msPastDuration = Date.now() - Number(self.startTime) - Number(self.duration);


        if (msPastDuration < 0) {
        // we're still within the timeline
          loopUpdate(); 
        } else {
          // we're past timeline duration!
          if (self.loop) {
            self.completed_events = {};
            self.startTime = Date.now() - msPastDuration;
            loopUpdate();
          } else {
          // we're not looping and we're over
            if (opts && 'callback' in opts && typeof(opts.callback) === 'function') {
              opts.callback();
            }
          }
        }
      }, self.interval);
    };
    loopUpdate();
  }
}