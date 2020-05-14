


output_file = fopen('DCR_hsv_values.csv', 'w');

image_names = textread('image_list.txt', '%s');
fprintf(output_file, 'ImageSet,File,hue_mean,hue_sd,saturation_mean, saturation_sd,value_mean, value_sd\n');
for i = 1:length(image_names)
    img = imread(char(strcat('MethOpioidDatabase/finalcueset/ExtractedMethCues120/', image_names(i))));
    [h, s, v] = rgb2hsv(img);
    fprintf(output_file, '%s,%s,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f\n', 'meth', char(image_names(i)), mean(mean(h)), std2(h), mean(mean(s)), std2(s), mean(mean(v)), std2(v));
end

for i = 1:length(image_names)
    img = imread(char(strcat('MethOpioidDatabase/finalcueset/ExtractedNeutralCues120/', image_names(i))));
    [h, s, v] = rgb2hsv(img);
    fprintf(output_file, '%s,%s,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f\n', 'control', char(image_names(i)), mean(mean(h)), std2(h), mean(mean(s)), std2(s), mean(mean(v)), std2(v));
end

for i = 1:length(image_names)
    img = imread(char(strcat('MethOpioidDatabase/finalcueset/ExtractedOpioidCues120/', image_names(i))));
    [h, s, v] = rgb2hsv(img);
    fprintf(output_file, '%s,%s,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f\n', 'opioid', char(image_names(i)), mean(mean(h)), std2(h), mean(mean(s)), std2(s), mean(mean(v)), std2(v));
end


fclose(output_file);