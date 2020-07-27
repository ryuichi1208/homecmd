#include <stdio.h>
#include <string.h>

static char *ft_strncpy(char *dest, char *src, unsigned int n)
{
  unsigned int i;

  i = 0;
  while (i < n)
  {
    dest[i] = src[i];
    if (src[i] == '\0')
      break;
    i++;
  }
  if ((i < n) && (src[i] == '\0'))
  {
    while (dest[i] != '\0')
    {
      dest[i] = '\0';
      i++;
    }
  }
  return dest;
}

int main()
{
  char str1[100] = "12333";
  char str2[100] = "12333";

  char zero[] = "";
  char symbol[] = ",.;:;";
  char space[] = "hello world";
  char nb[] = "12345";
  char escape[] = "\n";
  char eos[] = "\0";
  char nbandstr[] = "12fj3j4f";
  char eosinstr[] = "aaa\0aaa";

  strncpy(str1, zero, 1);
  ft_strncpy(str2, zero, 1);
  printf("%s %s\n", str1, str2);

  strncpy(str1, symbol, 1);
  ft_strncpy(str2, symbol, 1);
  printf("%s %s\n", str1, str2);

  strncpy(str1, space, 1);
  ft_strncpy(str2, space, 1);
  printf("%s %s\n", str1, str2);

  strncpy(str1, nb, 1);
  ft_strncpy(str2, nb, 1);
  printf("%s %s\n", str1, str2);

  strncpy(str1, escape, 1);
  ft_strncpy(str2, escape, 1);
  printf("%s %s\n", str1, str2);

  strncpy(str1, eos, 1);
  ft_strncpy(str2, eos, 1);
  printf("%s %s\n", str1, str2);

  strncpy(str1, nbandstr, 1);
  ft_strncpy(str2, nbandstr, 1);
  printf("%s %s\n", str1, str2);

  strncpy(str1, eosinstr, 1);
  ft_strncpy(str2, eosinstr, 1);
  printf("%s %s\n", str1, str2);

  return 0;
}
