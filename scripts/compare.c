#include<stdio.h>
#include<stdlib.h>
#include<math.h>

int main()
{
    FILE *f1 = fopen("reference.ppm", "rb");
    FILE *f2 = fopen("compressed.ppm", "rb");
    FILE *out = fopen("diff.ppm", "wb");

    if (!f1 || !f2 || !out)
    {
        printf("File error\n");
        return 1;
    }

    // Read headers (assumes same format)
    char header[3];
    int width, height, maxval;

    fscanf(f1, "%s\n%d %d\n%d\n", header, &width, &height, &maxval);
    fscanf(f2, "%s\n%d %d\n%d\n", header, &width, &height, &maxval);

    // Write output header
    fprintf(out, "P6\n%d %d\n%d\n", width, height, maxval);

    for(int i = 0; i < width * height * 3; i++)
    {
        unsigned char p1 = fgetc(f1);
        unsigned char p2 = fgetc(f2);

        int diff = abs(p1 - p2);

        // amplify difference for visibility
        diff = diff * 4;
        if(diff > 255) diff = 255;

        fputc(diff, out);
    }

    fclose(f1);
    fclose(f2);
    fclose(out);

    printf("Difference image created: diff.ppm\n");
    return 0;
}
