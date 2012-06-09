function slide() {
	jQuery('.kwicks').kwicks({
		max : 600
	});
	jQuery('.slide').bind({
		mouseenter: function() {
			var slide = jQuery(this);
			var opacity = jQuery('.opacity', slide);
			var container = jQuery('.entry-container', slide);
			opacity.stop(true, true).fadeOut(500);
			container.stop(true, true).delay(500).fadeIn(500);
		},
		mouseleave: function() {
			var slide = jQuery(this);
			var opacity = jQuery('.opacity', slide);
			var container = jQuery('.entry-container', slide);
			opacity.stop(true, true).fadeIn(500);
			container.stop(true, true).hide(500);
		}
	});
}

jQuery().ready(function() {
	slide();
	jQuery('.nav a').bind({
		mouseenter:function() {
			jQuery(this).animate({
				marginTop: -5
			});
		},
		mouseleave:function() {
			jQuery(this).animate({
				marginTop: 0
			});
		}
	});
	jQuery('.entry-tags a').bind({
		mouseenter:function() {
			jQuery(this).animate({
				top: -2
			}, 100);
		},
		mouseleave:function() {
			jQuery(this).animate({
				top: 0
			}, 100);
		}
	});
});
