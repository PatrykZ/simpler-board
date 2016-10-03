'use strict';

var gulp = require('gulp'),
    rename = require('gulp-rename'),
    sass = require('gulp-sass');

gulp.task('sass', function () {
    return gulp.src('src/stylesheets/*.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('dist/stylesheets/'));
});

gulp.task('watch', function() {
    gulp.watch('src/stylesheets/**/*.scss', ['sass'])
});

gulp.task('default', ['watch', 'sass']);