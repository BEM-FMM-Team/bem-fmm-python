cases = {};

cases{end+1} = struct('name','single_tri_single_obs', ...
    'r1', [0 0 0], 'r2', [1 0 0], 'r3', [0 1 0], 'obsPoint', [0.1 0.1 0.2]);

cases{end+1} = struct('name','single_tri_multi_obs', ...
    'r1', [0 0 0], 'r2', [1 0 0], 'r3', [0 1 0], 'obsPoint', [0.1 0.1 0.2; 0.5 0.5 1.0; 2 2 2]);

cases{end+1} = struct('name','multi_tri_single_obs', ...
    'r1', [0 0 0; 0 0 1], 'r2', [1 0 0; 1 0 1], 'r3', [0 1 0; 0 1 1], 'obsPoint', [0.2 0.2 0.5]);

cases{end+1} = struct('name','multi_tri_multi_obs', ...
    'r1', [0 0 0; 0 0 1; 1 0 0], 'r2', [1 0 0;1 0 1;2 0 0], 'r3', [0 1 0;0 1 1;1 1 0], ...
    'obsPoint', [0.1 0.1 0.2; 0.9 0.1 0.2; 0.5 0.5 0.5]);

cases{end+1} = struct('name','on_vertex', ...
    'r1', [0 0 0], 'r2', [1 0 0], 'r3', [0 1 0], 'obsPoint', [0 0 0]);

cases{end+1} = struct('name','degenerate', ...
    'r1', [0 0 0], 'r2', [1 1 1], 'r3', [2 2 2], 'obsPoint', [1 0 0]);

for k = 1:numel(cases)
    c = cases{k};
    fprintf('CASE: %s\n', c.name);
    disp('r1:'); disp(c.r1); disp('r2:'); disp(c.r2); disp('r3:'); disp(c.r3);
    disp('obsPoint:'); disp(c.obsPoint);
    try
        out = potint4b(c.r1, c.r2, c.r3, c.obsPoint);
        disp('output:'); disp(out);
        success = 1;
    catch ME
        fprintf('ERROR: %s\n', ME.message);
        success = 0;
    end
    fprintf('success: %d\n', success);
    fprintf('%s\n', repmat('-',1,80));
end
